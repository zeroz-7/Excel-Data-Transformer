# Quick User Guide: Writing Effective Data Transformation Prompts

## 🎯 **Simple Rules for Better Results**

### 1. **One Instruction Per Line**
**✅ DO THIS:**
```
Merge all Excel files
Convert DL_Volume columns to numbers
Replace -8888 with blanks in volume columns
Sum volume columns into Total_traffic
Replace NA values in signal columns with blanks
Extract numbers from RF_RSRP_Desc after "<" symbol
Split unique_trace_reference by "_" into mnc, gnb, cnum
Calculate A3 = target_RSRP - source_RSRP
```

**❌ NOT THIS:**
```
1,merge files 2,convert numbers 3,replace -8888 4,sum columns
```

### 2. **Use Clear Column Names**
**✅ SPECIFIC:**
```
Replace -8888 in DL_Volume_5QI1_towards_UE
Extract numbers from RF_RSRP_Desc
Split unique_trace_reference
```

**❌ VAGUE:**
```
Fix volume columns
Clean text columns
Process IDs
```

### 3. **Specify What to Replace**
**✅ CLEAR:**
```
Replace -8888 with blanks
Replace NA with empty strings
Replace 0 with blanks in RF_Avg_CQI
Replace -156 in source_RSRP
```

**❌ UNCLEAR:**
```
Remove bad values
Clean invalid data
Fix errors
```

### 4. **Explain Calculations Simply**
**✅ UNDERSTANDABLE:**
```
Sum DL_Volume columns into Total_traffic
Calculate A3 = target_RSRP - source_RSRP
Keep only A3 values >= 3
```

**❌ CONFUSING:**
```
Make total traffic
Do A3 calculation
Filter results
```

## 📝 **Perfect Quick Prompt Format**

```
Merge all Excel files
Convert these to numbers: DL_Volume_5QI1_towards_UE, UL_Volume_5QI1_from_UE, DL_Volume_5QI2_towards_UE, UL_Volume_5QI2_from_UE
Replace -8888 with blanks in the above volume columns
Sum the four volume columns into Total_traffic column
Replace NA with blanks in: RF_RSRP_Desc, RF_RSRQ_Desc, RF_Avg_CQI, Mobility_RSRP_1_Desc
Extract numbers after "<" from RF_RSRP_Desc into source_RSRP
Extract numbers after "<" from RF_RSRQ_Desc into source_RSRQ  
Extract numbers after "<" from Mobility_RSRP_1_Desc into target_RSRP
Replace 0 with blanks in RF_Avg_CQI
Split unique_trace_reference by "_" into mnc, gNB ID, cnum
Calculate A3 = target_RSRP - source_RSRP
Keep only A3 values >= 3
```

## 💡 **Pro Tips for Non-Coders**

### **Be Specific About:**
- **Column names** exactly as they appear
- **Values to replace** (-8888, NA, 0, etc.)
- **New column names** you want to create
- **Simple calculations** (sum, difference, etc.)

### **Avoid:**
- Technical terms like "regex", "dataframe", "merge"
- Complex formulas
- Assuming the bot knows your data structure

## 🚀 **Example That Works Well**

```
Process all uploaded Excel files
Convert these to numbers: Sales_Amount, Quantity, Discount
Replace -999 with blanks in the above columns
Sum Sales_Amount and Quantity into Total_Value
Replace NA with blanks in: Customer_Name, Product_Code, Category
Extract area code from Phone_Number into Area_Code
Split Customer_ID by "-" into Region, Store, ID
Calculate Profit = Revenue - Cost
Keep only Profit values > 0
```

This format is easy for users to write and gives the AI clear, actionable instructions!
