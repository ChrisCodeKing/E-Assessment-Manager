# QTI Test Manager Help

Welcome to the QTI Test Manager Help Guide. This guide will assist you in managing your assessments efficiently.

## Uploading Assessments

To upload an assessment:

1. Click the **"Upload"** button.

2. Select the assessment file in `.xml` format. 

    **Note:** Only one file can be uploaded at a time.

The system validates the XML file against the SAKAI QTI 1.2 implementation. If the validation fails, the upload will not succeed. Ensure that your XML file is correctly formatted.

## Jobs Overview

The Jobs Overview displays all currently loaded assessments. For each assessment, you can see:

- **Name** of the assessment

**Buttons**:

  - **View/Edit**: Opens the assessment for viewing or editing.

  - **Remove**: Deletes the assessment.

  - **Export**: Allows you to export the assessment.

## Creating Assessments

To create a new assessment:

1. Click **"Create Test"**.

2. Enter the title of the assessment.

3. Select the desired question type from the drop-down menu.

4. Click the **"Add"** button to open a new window.

5. In the new window, input the question text, answers, and solutions in JSON format:
    - **Answers Example**: `{"A": "Answer here", "B": "Answer here", ...}`
    - **Solutions Example**: `{"A": "Incorrect", "B": "Correct", "C": "Incorrect", "D": "Incorrect"}`

6. Click **"Save"** to add the question to the assessment.

7. Once all questions are added, click **"Save"** again. The test will be added to the Assessment Overview.

## Editing Assessments

To edit an existing assessment:

1. Click the **"View/Edit"** button in the Assessment Overview.

2. Modify the questions as needed, similar to the creation process.

3. Click **"Save"** to update the assessment.

## Removing Assessments

To remove an assessment:

1. Click the **"Remove"** button in the Assessment Overview.

2. Confirm the removal. The assessment will be deleted from the Assessment Overview.

## Exporting Assessments

To export an assessment:

1. Click the **"Export"** button in the Assessment Overview.

2. Choose the desired export format:
    - **IMS Content Packaging**: Exports an archive package, which includes the assessment metadata and the QTI 1.2 XML file.
    - **QTI 1.2 SAKAI implementation**: Exports only the QTI XML file.

In the future additional formats will be supported for exporting assessments, such as Excel. 

Follow these steps to efficiently manage your assessments using the QTI Test Manager.
