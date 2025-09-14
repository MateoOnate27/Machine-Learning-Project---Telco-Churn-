# 📊 Telco Customer Churn — Interactive EDA (Streamlit)

This project is an interactive web application built with **Streamlit**, designed to explore the **Telco Customer Churn** dataset.  
The goal is to perform an **Exploratory Data Analysis (EDA)** to discover patterns related to customer churn, supported with **KPIs, interactive filters, and dynamic visualizations**.

---

## 🚀 Main Features
- **Dynamic data upload**: upload the original Telco CSV file.  
- **Interactive filters** to segment information by:
  - Contract type (`Contract`)  
  - Payment method (`PaymentMethod`)  
  - Internet service (`InternetService`)  
  - Gender, Partner, Dependents, SeniorCitizen  
  - Range of `tenure` (customer months)  
  - Range of `MonthlyCharges` (monthly fees)  
- **Key Performance Indicators (KPIs):**
  - 📉 Churn rate (%)  
  - 💵 Average monthly charges  
  - 🗓️ Average tenure  
  - 👥 Total filtered customers  
- **Dynamic visualizations with Plotly:**
  - Churn distribution pie chart  
  - Histograms of `tenure` and `MonthlyCharges` (colored by churn)  
  - Bar chart: churn by selected categorical variable  
  - Crossed churn heatmap: churn rate by category combinations  
  - Boxplot of `MonthlyCharges` vs `Churn`  
  - Scatter plot `tenure` vs `MonthlyCharges`  
  - Correlation heatmap (auto-conversion of Yes/No to 1/0)  
- **Key findings section** to summarize insights.

---

## 📦 Installation and Execution

### 1. Clone repository or copy files
Make sure you have the following files in your working directory:
- `app.py` (Streamlit application)  
- `requirements.txt` (dependencies)  
- `README.md` (this file)  

### 2. Create virtual environment (optional, recommended)
```bash
python -m venv venv
# Activate environment
venv\Scripts\activate      # On Windows
source venv/bin/activate     # On Linux/Mac
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
streamlit run app.py
```

### 5. Open in browser
The terminal will display a link such as:  
👉 [http://localhost:8501](http://localhost:8501)  

---

## 📂 Expected Dataset
The project is designed to work with the **Telco Customer Churn** dataset from Kaggle or IBM:  
- Typical file: `WA_Fn-UseC_-Telco-Customer-Churn.csv`  

Upload the CSV to the app using the **uploader** at the beginning.

---

## 📌 Example Findings
- Customers with **month-to-month contracts** have higher churn rates compared to 1- or 2-year contracts.  
- Higher **MonthlyCharges** are often associated with higher churn probability.  
- Customers with **low tenure (less than 12 months)** concentrate most churn cases.  
- Payment methods such as **Electronic check** are correlated with higher churn rates.  

---