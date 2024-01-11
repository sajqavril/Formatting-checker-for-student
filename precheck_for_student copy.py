from data_models import *
from utils import _compare, _get_right_formatting_answer_path

def precheck_for_student(andrew_id, student_file_path, lab_index):
    """
    Used by SINGLE student for self-prechecking purpose before submitting their submissions
    @param andrew_id
    @param student_file_path: the path of the student's submission, and the file name ends up with .Collection
    @param lab_indx, int, to locate the corresponding answer_file in the package, which is inaccessible to students
    """
    right_formatting_answer_path = _get_right_formatting_answer_path(lab_index=lab_index) # get the actual file, not a path
    errors = _compare(andrew_id=andrew_id,
            student_answer_path=student_file_path,
            right_formatting_answer_path=right_formatting_answer_path)
    if errors == None:
        print("Congratulations! Your submission is correctly formatted and ready for Canvas!")
        return
    else:
        print("There is at least one formatting error in your submission, please correct:")
        for error in errors:
            print(error)
        print("Keep returning to this precheck process until there are no formatting errors before submitting to Canvas!")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--andrew-id', type=str, required=True)
    parser.add_argument('--student-file-path', type=str, required=True, help="Absolute path of your answer in your PC")
    parser.add_argument('--lab-index', type=int, required=True, help="Please indicate which lab you are submitting")    
    
    args = parser.parse_args()
    
    precheck_for_student(andrew_id=args.andrew_id, 
                         student_file_path=args.student_file_path,
                         lab_index=args.lab_index)
    
if __name__ == "__main__":
    main()
    

