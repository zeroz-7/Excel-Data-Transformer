import tempfile
import os
import json
import sys
import logging

# Add the backend directory to Python path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

try:
    from crewai_app.custom_tool import excel_data_inspector_tool
    print("✅ Successfully imported excel_data_inspector_tool")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Trying alternative import...")
    try:
        # Try direct import if the structure is different
        from custom_tool import excel_data_inspector_tool
        print("✅ Successfully imported via direct import")
    except ImportError:
        print("❌ Both import methods failed")
        print("Current directory:", os.getcwd())
        print("Python path:", sys.path)
        exit(1)

def test_file_access():
    """Test if the tool can access files - MANUAL FILE PATHS VERSION"""
    
    # MANUALLY PLUG YOUR EXCEL FILE PATHS HERE:
    test_files = [
        r"C:\Users\Anush\Downloads\t1.xlsx",  # ← REPLACE with your actual file path
        r"C:\Users\Anush\Downloads\t2.xlsx",  # ← REPLACE with your actual file path
        r"C:\Users\Anush\Downloads\t3.xlsx",  # ← REPLACE with your actual file path        
        # Add more files as needed
    ]
    
    print("🧪 Testing with manually specified files:")
    for file_path in test_files:
        print(f"   - {file_path}")
        if os.path.exists(file_path):
            print("     ✅ File exists")
        else:
            print("     ❌ File NOT found")
    
    print(f"\n🔍 Starting inspection of {len(test_files)} files...")
    result = excel_data_inspector_tool._run(test_files)
    
    print("\n" + "="*50)
    print("TOOL RESULT (JSON):")
    print("="*50)
    
    try:
        parsed_result = json.loads(result)
        print(json.dumps(parsed_result, indent=2))
        
        # Print summary
        print("\n" + "="*50)
        print("SUMMARY:")
        print("="*50)
        if 'files' in parsed_result:
            for file_info in parsed_result['files']:
                status = file_info.get('status', 'unknown')
                if status == 'success':
                    print(f"✅ SUCCESS: {file_info['resolved_path']}")
                    print(f"   📊 Shape: {file_info['metadata']['rows']} rows × {file_info['metadata']['columns']} columns")
                    print(f"   📋 Columns: {len(file_info['columns'])}")
                    print(f"   👀 Preview: {len(file_info['preview'])} rows")
                    if file_info['columns']:
                        print(f"   🏷️  First few columns: {[col['name'] for col in file_info['columns'][:3]]}")
                elif status == 'error':
                    print(f"❌ ERROR: {file_info.get('original_path', 'Unknown')}")
                    print(f"   💬 Error: {file_info.get('error', 'Unknown error')}")
                else:
                    print(f"⚠️  {status.upper()}: {file_info.get('original_path', 'Unknown')}")
        
        if parsed_result.get('errors'):
            print(f"\n❌ Errors encountered: {len(parsed_result['errors'])}")
            for error in parsed_result['errors']:
                print(f"   - {error}")
                
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON response: {e}")
        print(f"Raw response: {result}")

def test_with_temp_files():
    """Alternative: Test with files from temp directory"""
    temp_dir = tempfile.gettempdir()
    print(f"\n📁 Checking temp directory: {temp_dir}")
    
    # List all Excel files in temp dir
    excel_files = [f for f in os.listdir(temp_dir) if f.endswith(('.xlsx', '.xls'))]
    print(f"📊 Excel files in temp dir: {excel_files}")
    
    if excel_files:
        test_files = [os.path.join(temp_dir, excel_files[0])]
        print(f"🧪 Testing with temp file: {test_files[0]}")
        result = excel_data_inspector_tool(test_files)
        
        try:
            parsed_result = json.loads(result)
            print("✅ Temp file test completed successfully")
        except json.JSONDecodeError:
            print("❌ Temp file test failed")

if __name__ == "__main__":
    print("Choose test mode:")
    print("1. Test with MANUAL file paths (edit code)")
    print("2. Test with files from TEMP directory")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_file_access()
    else:
        test_with_temp_files()