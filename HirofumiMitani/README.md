# Hirofumi Mitani's Work

🇺🇸 English | [🇯🇵 日本語](./README_JPN.md)  
This directory contains the research notebooks\* by Hirofumi Mitani during the FY2025 Laboratory Research, a third-year course at the Faculty of Medicine, Tokushima University.  
(\*Limited to the publicly shareable ones)  

## Research Project

### Objective
The purpose of this study is to create a cancer classisication model using data form the J-MICC Study and investigate its association with oral and upper gastrointestinal cancers.

### methods
From the J-MICC Study, oral and upper gastrointestinal cancer patients and a control group(n=1,546 1:1)matched for propensity scores such as age and sex were selected as study subjects.
We then constructed a machine learning model to classify cancer and non-cancer cases from the nutritional data of the control group and evaluated the importance of features in the model.

### results
The accuracy of the random forest model built using energy-adjusted nutrient data was 0.56,and the accurecy of the random forest model built using the adjusted nutrient data's principal component scores was 0.55.
Furthermpore, Shapley Additive Explantations values showed relativaly high for carbohydrates, monounsaturated fatty acid, and calcium.

### Discussion
This random forest model had low discrimination accuracy, indicating that the nutrient intake data used in this study alone can not adequately predict the incidence of oral and upper gastrointestinal cancer.
One possible interpretation of there results is that other risk factors outweighed the effects of the study.
To assess the effects of nutrients, it is anticipated that future work will inovlve adjusted for cinfounding factors and incorporating them into the model.

## Notebooks
### code_1

・Extraction of necessary data

・Converting missing values

・Unifying data types

・Creating new data columns(BMI, physical activity)

・Removing excess energy data

・Extraction of Follow-Up Data

・Deletion of Data with Early Onset and History of Disease

・Extraction of cancer patients

### code_2

・Distortion Removal

・Energy Adjustment

### code_3

・Propensity score matching (PSM)

・T-test, K-S test, Fisher test, Wilcoxon test

### code_4

・Standardization

・Principal Component Analysis (PCA)

### code_5

・Creating training and testing data sets (80:20)

・Optimizing hyperparameters for random forests

・Accuracy

・Confusion matrix

・ROC curve

・SHAP

## Requirement, Licence, Acknowledgement, etc.

1. Douglas E Morse et al. Cancer Causes Control (2007)
2. Mizuki Ohash et al. Hypertens Res(2022)
3. Jun Wu et al. Front Pharmacol(2024)
4. Yukiko Yano et al. Cancer Prev Res (Phila)(2021)
5. Wenmin Liu et al.Nutrients (2023)
6. Ho D E et al. J Stat Softw (2021)
7. Lundberg S M & Lee S-I et al. NeurIPS Proceedings (2017)


## Log
- Created this directory: Oct. 24, 2025 (Kengo Watanabe)
- Uploaded the notebooks: Oct. 28, 2025 (Hirofumi Mitan)
