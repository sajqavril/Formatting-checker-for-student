from data_models import *

def _get_file_name(path):
        path = os.path.split(path)
        return path[-1]

# for formatting only
def _compare(andrew_id, student_answer_path, right_formatting_answer_path, tmp_directory=None):
    """
    Detect format failures of two .Collection files
    Specifically, for all TextGrid in the right answer, 
    except the ones that have suffix of "-error-bound",
    to see in student_answer, if contains such file have the identical name and correct format

    @param andrew_id
    @param student_answer_path: the abspath of student submission
    @param right_formatting_answer_path: the relative/internal formatting answer file within the program
    @param tmp_directory: the temporar directory to store the intermediate-stage .txt files
    """

    assert os.path.isfile(student_answer_path), "You should input a valid file path, {:s} cannot be found!".format(student_answer_path)
    assert os.path.isabs(student_answer_path), "You should input an absolute file path, {:s} is not satisfied!".format(student_answer_path)

    errors = []
    # First, to detect if there is any file name's mismatching error 
    student_answer_name = _get_file_name(student_answer_path)
    right_formatting_answer_name = _get_file_name(right_formatting_answer_path)
    
    expected_student_answer_name = "{:s}_{:s}".format(andrew_id, right_formatting_answer_name)

    if expected_student_answer_name != student_answer_name:
        error_collection_name = "Your uploaded file name {:s} does not follow the instructions, please rename it.".format(student_answer_name)
        errors.append(error_collection_name)
        

    # Second, convert both .Collection files into .txt and read both as Collection objects
    if tmp_directory == None:   # if the tmp_directory is not given, then it means the portal that calls this function is precheck_for_student,
                                # otherwise, the precheck_for_teacher will explicitly provide a directory to make sure all the intermediate files are stored in one directory
        datestr = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        tmp_directory = os.path.join(os.path.abspath("."), ("Precheck_for_student_" + datestr))
        assert not os.path.isdir(tmp_directory), "Something went wrong, {:s} has been taken!".format(tmp_directory)
        os.mkdir(tmp_directory)

    student_txt_path = tmp_directory +  "/" + andrew_id + ".txt" 
    answer_txt_path = tmp_directory + "/" + "answer.txt"
    pm.read(student_answer_path).save_as_text_file(student_txt_path)
    pm.read(right_formatting_answer_path).save_as_text_file(answer_txt_path)
    student_answer_txt = open(student_txt_path).read()
    right_answer_txt = open(answer_txt_path).read()
    os.remove(answer_txt_path)
    os.remove(student_txt_path)

    try:
        tmp1 = student_answer_txt.index("ooTextFile")
        tmp2 = right_answer_txt.index("ooTextFile")
    except:
        error_ootextfile_type = "Abortion: only ooTextFile file type can be processed! Else file type is detected!"
        errors.append(error_ootextfile_type)
        return NotImplementedError
    student_answer_obj = Collection(student_answer_txt)
    right_answer_obj = Collection(right_answer_txt)

    # Thirdly, follow the order of the TextGrid files in right answer, check the possible format errors of student answer
    for item in right_answer_obj.items:
        if item.classid == TEXTGRID:
            textgrid = item
            matched_textgrid = None
            for student_item in student_answer_obj.items:
                if student_item.classid == TEXTGRID and student_item.nameid == textgrid.nameid:
                    matched_textgrid = student_item
                    for tier in textgrid.tiers:
                        if tier.classid == INTERVALTIER:
                            interval = tier
                            matched_tier = None
                            for student_tier in matched_textgrid.tiers:
                                if student_tier.classid == INTERVALTIER and student_tier.nameid == interval.nameid:
                                    matched_tier = student_tier
                                    if len(interval.tier_labels) != len(matched_tier.tier_labels):
                                        error_num_interval_mismatch = "There are {:d} intervals detected; {:d} are expected in Interval Tier named {:s} in TextGrid file named {:s}".format(
                                                  len(matched_tier.tier_labels)-2,
                                                  len(interval.tier_labels)-2,
                                                  interval.nameid,
                                                  textgrid.nameid)
                                        errors.append(error_num_interval_mismatch)
                                        
                                    else:
                                        interval_labels_nameid = [l[2] for l in interval.tier_labels]
                                        interval_labels_nameid.sort()
                                        matched_tier_labels_nameid = [l[2] for l in matched_tier.tier_labels]
                                        matched_tier_labels_nameid.sort()
                                        for i in range(len(interval.tier_labels)):
                                            if interval_labels_nameid[i] != matched_tier_labels_nameid[i]:
                                                error_name_interval_mismatch = "The name of the Interval Tier does not follow instructions (mismatched) in Interval Tier named {:s} of TextGrid file named {:s}".format(
                                                          interval.nameid,
                                                          textgrid.nameid
                                                      )
                                                errors.append(error_name_interval_mismatch)
                                                
                            if matched_tier == None:
                                error_interval_tier_not_found = "Interval Tier named {:s} not found in TextGrid file named {:s}!".format(interval.nameid, matched_textgrid.nameid)
                                errors.append(error_interval_tier_not_found)
                                    
                                
                        else: 
                            assert tier.classid == TEXTTIER
                            try:
                                tmp = tier.nameid.index("-error-bound") # skip the texttier using as error bars
                            except:
                                point = tier
                                matched_tier = None
                                for student_tier in matched_textgrid.tiers:
                                    if student_tier.classid == TEXTTIER and student_tier.nameid == point.nameid:
                                        matched_tier = student_tier
                                        if len(point.tier_labels) != len(matched_tier.tier_labels):
                                            error_num_point_mismatch = "There are {:d} points detected; {:d} are expected in Point Tier named {:s} in TextGrid file named {:s}".format( 
                                                    len(matched_tier.tier_labels),
                                                    len(point.tier_labels),
                                                    point.nameid,
                                                    textgrid.nameid)
                                            errors.append(error_num_point_mismatch)
                                            
                                        else:
                                            point_labels_nameid = [l[1].split("=")[0].strip() for l in point.tier_labels]
                                            point_labels_nameid.sort()
                                            matched_tier_labels_nameid = [l[1].split("=")[0].strip() for l in matched_tier.tier_labels]
                                            matched_tier_labels_nameid.sort()
                                            for i in range(len(point.tier_labels)):
                                                if point_labels_nameid[i] != matched_tier_labels_nameid[i]:
                                                    error_name_point_mismatch = "The name of the Point Tier does not follow instructions (mismatched) in Point Tier named {:s} of TextGrid file named {:s}".format(
                                                            point.nameid,
                                                            textgrid.nameid
                                                        )
                                                    errors.append(error_name_point_mismatch)
                                                    
                                if matched_tier == None:
                                    error_point_tier_not_found = "Point Tier named {:s} is not found in TextGrid file named {:s}!".format(point.nameid, matched_textgrid.nameid)
                                    errors.append(error_point_tier_not_found)
                                                                      
            if matched_textgrid == None:
                error_textgrid_not_found = "TextGrid file named {:s} not found!".format(item.nameid)
                errors.append(error_textgrid_not_found)
    
    if tmp_directory.__contains__("for_student"):
        os.removedirs(tmp_directory)

    if len(errors) > 0:
        return errors
    return None


def _get_right_answer_path(lab_index):
    """
    Get the relative path of the right answer within the executible program, compiled in advance, and not accessible for users 
    The name of the right answer corresponding to the lab_index x should contains a substring of "Labx"
    """
    assert type(lab_index) == int, "You need to input an integer to identify which Lab your submission belongs to!"
    right_answer_path = "{:s}/Answers/Lab{:d}.Collection".format(BASE_DIR, lab_index)
    assert os.path.isfile(right_answer_path), "Error! There is an error when locating the right answer {:s}, the program now is in {:s}".format(right_answer_path, BASE_DIR) 
        
    return right_answer_path

def _get_right_formatting_answer_path(lab_index):
    """
    Get the relative path of the right answer within the executible program, compiled in advance, and not accessible for users 
    The name of the right answer corresponding to the lab_index x should contains a substring of "Labx"
    """
    assert type(lab_index) == int, "You need to input an integer to identify which Lab your submission belongs to!"
    right_formatting_answer_path = "{:s}/formatting_answers/Lab{:d}.Collection".format(BASE_DIR, lab_index)
    assert os.path.isfile(right_formatting_answer_path), "Error! There is an error when locating the right answer {:s}, the program now is in {:s}".format(right_answer_path, BASE_DIR) 
        
    return right_formatting_answer_path

def _get_student_andrew_id_list():
    return STUDENT_ANDREW_ID_LIST

def _tier_obj_dict_to_textgrid(tier_obj_dict, directory, max_tier=3):
    """
    Transfer the dictionary of interval tier objects into .TextGrid files

    @param tier_obj_dict, for example: 
                        key: "Mandarin_mother", "Segment"
                        value: [answer_tier_obj, student1_tier_obj, student2_tier_obj, ...] 
    @param directory: path to store the generated files, set as the tmp_directory by grading program
    @param max_tier: the maximal number of tiers contains in one textgrid file, the answer tier is not counted and will always show on the top of the textgrid file
    """
    assert os.path.isdir(directory), "Error! Please provide a valid directory to save the generated segmentation answers, {:s} should be replaced!".format(directory)

    for textgrid_name, tg_dict in tier_obj_dict.items():
        for tier_name, tier_list in tg_dict.items(): 
            answer = tier_list.pop(0)
            rearranged_tier_list = [[] for i in range(len(tier_list) // max_tier + 1)]
            for j in range(len(rearranged_tier_list)-1):
                rearranged_tier_list[j].append(answer)
                rearranged_tier_list[j].extend(tier_list[j*max_tier : (j+1)*max_tier])
            rearranged_tier_list[-1].append(answer)
            rearranged_tier_list[-1].extend(tier_list[(len(rearranged_tier_list)-1)*max_tier : ])

            for idx, list_txt in enumerate(rearranged_tier_list):
                filename = "{:s}_{:s}_{:d}({:d}).TextGrid".format(textgrid_name, tier_name, idx+1, len(rearranged_tier_list))
                header = open("{:s}/seg_answer_header.txt".format(BASE_DIR)).read()
                header = header.replace("xmin = 0", "xmin = {:f}".format(list_txt[0][1].xmin))
                header = header.replace("xmax = 1", "xmax = {:f}".format(list_txt[0][1].xmax))
                header = header.replace("size = 0", "size = {:d}".format(len(list_txt)))
                content = [header]
                for idx_item, item in enumerate(list_txt):
                    content.append("    item [{:d}]:".format(idx_item+1))
                    item_txt = item[1].tier_text
                    item_txt = item_txt.replace("name = \"{:s}\"".format(tier_name), "name = \"{:s}\"".format(item[0]))
                    item_txt = item_txt.split("\n")
                    item_txt.pop(0)
                    item_txt.pop(0)
                    item_txt = [t[8:] for t in item_txt]
                    content.extend(item_txt)
                content = "\n".join(content)
                with open(os.path.join(directory, filename), "w") as f:
                    f.write(content)
                    f.close()
