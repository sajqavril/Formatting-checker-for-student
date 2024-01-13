# Overview

Welcome to the automatic formatting checker developed for the course _Acoustics of Human Speech: Theory, Data, and Analysis (80-788) at Carnegie Mellon University. Since this software is for teaching purposes only, if you would like to contribute/refer to this work, please contact the instructor [Christina Bjorndahl](https://christinabjorndahl.com) via [cbjorn@andrew.cmu.edu](cbjorn@andrew.cmu.edu). And during the whole semester of this class, we also have an assistant Jiaqi Sun to help the students to use this tool. So if there are any questions that the students encountered while installing/using this tool, please feel free to contact [Jiaqi Sun](https://www.cmu.edu/dietrich/philosophy/people/masters/jiaqi-sun.html) at [jiaqisun@andrew.cmu](jiaqisun@andrew.cmu) or schedule an offline meeting by email.

Students who are taking this course in the spring semester of 2024 or in the following semesters are strongly encouraged to use this tool to check the format of each of your submissions. Because in this course most of the assignments should be done by the software [Praat](https://www.fon.hum.uva.nl/praat/), and also we are using auto-grading tool to grade all submissions, the correct format is necessary and essential for your submissions to get _positive_ scores. 

# Instructions (for students)
When using this tool to check the format, each submission should be a .Collection file composed of several .TextGrid files. 

After each assignment is approved (when the correctly formatted answer template is uploaded) and before each assignment is due, students are free to try this tool until there are no more errors in their submission. Remember that only the error-free .TextGrid files in a submission can possibly be graded positively. 

There are two ways to use this tool. 

## Option 1: Execute Python source code (recommended)
This is the most recommended because it is independent of what platforms your PC is, i.e. MacOS, Windows, and Linux. And the environment to run Python is super easy to install.

1. Make sure you have [```Python >= 3.8```](https://realpython.com/installing-python/) on your PC and the download tool [```pip```](https://pip.pypa.io/en/stable/getting-started/).
2. Download the package from git or directly from your web browser.
3. Move the whole package to the target directory where you want to put this tool in your PC and unzip it.
4. Specify the top-level directory of the package.
5. Install all the required packages specified in the requirements.txt file. This is done with the following command
   ```sh
   pip install -r requirements.txt
   ```
6. Execute the following code with three parameters:
   1. your_andrew_id: your unique Andrew ID.
   2. your_submission_path: the absolute path to your submission; if there are spaces in the address, please add a backslash before each space.
   3. lab-index: an integer that indicates which lab you are checking the format against, e.g. input 1 if you are doing the first lab.
   ```sh
   python precheck_for_student.py --andrew-id your_andrew_id  --student-file-path your_submission_path  --lab-index lab_index
   ```
7. If there is no error, you will see an output of :
   ```
   Congratulations! Your submission is correctly formatted and ready for Canvas!
   ```
   Otherwise, you will see a list of all errors, and you should correct your submission and return to this Pre-Check tool until there are no more formatting errors before submitting. The following is an example of such a message.
   ```
   There is at least one formatting error in your submission, please correct:
   The name of the Interval Tier does not follow instructions (mismatched) in Interval Tier named Dorsum of TextGrid file named D2_dorsum
   The name of the Interval Tier does not follow instructions (mismatched) in Interval Tier named Lips of TextGrid file named D2_lip
   There are 19 intervals detected; 21 are expected in Interval Tier named Tip in TextGrid file named D2_tip
   The name of the Interval Tier does not follow instructions (mismatched) in Interval Tier named Dorsum of TextGrid file named A1_dorsum
   The name of the Interval Tier does not follow instructions (mismatched) in Interval Tier named Lips of TextGrid file named A1_lips
   There are 21 intervals detected; 23 are expected in Interval Tier named Tip in TextGrid file named A1_tip
   Keep returning to this precheck process until there are no formatting errors before submitting to Canvas!
   ```

For Windows users, if you have trouble when importing parselmouth package, you may try to unload, referring to [this tutorial]().

## Option 2: Run executable files 
This second option frees the students from installing the environments to run Python, and there are only three steps:

1. Download the ```dist-$$/``` directory of this package, choosing ```$$``` for your platform, and then move it to the desired location on your PC. If there does not have a version that matches your platform, please try option 1 or contact Jiaqi.
2. Go to the directory ```dist-$$/precheck_for_student/``` and run the executable with the same three parameters:
   1. your_andrew_id: your unique Andrew ID.
   2. your_submission_path: the absolute path to your submission; if there are spaces in the address, please add a backslash before each space.
   3. lab-index: an integer that indicates which lab you are checking the format against, e.g. input 1 if you are doing the first lab.
   ```sh
   $$$$$ --andrew-id your_andrew_id  --student-file-path your_submission_path  --lab-index lab_index
   ```
   and replace ```$$$$$``` with the choices below that matches your platform:

    - MacOS: ```./precheck_for_student```
    - Windows: ```precheck_for_student.exe```
    - Linux: ```./precheck_for_student```
 
Although it sounds more convenient to use executable files, because the compilation process is done by different platforms and computer architectures are of great variaty, it is possible that the executable file is not compatible with your platform. If you encounter this problem, please try option 1 or contact Jiaqi.

Finally, you may also encounter with the permission problem when trying to run it. If you are using MacOS, you can run the following code to turn off the Security Assessment Policy subsystem to make the executable run on your computer.


```
sudo spctl --master-disable
``` 

For Linux users, you should change the permission of the executable or the whole directory by running:
```
chmod +x precheck_for_student.exe
```

For Windows users, if you encounter such a permission issue that you cannot handle, please contact Jiaqi with a screenshot of the errors returned.


