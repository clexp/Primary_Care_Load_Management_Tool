#!/usr/bin/env python3
"""
Test script to verify the DES Modeler and Erlang Calculator pages work correctly
"""

import sys
import os

# Add the streamlit_app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'streamlit_app'))

def test_simulation_model_import():
    """Test that the simulation model can be imported without errors"""
    try:
        # Test importing the simulation model
        from simulation_model import run_multiple_simulations, CallCenterSimulation
        print("✅ Simulation model imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_des_modeler_page_import():
    """Test that the DES Modeler page can be imported without errors"""
    try:
        # Test importing the DES Modeler page
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "des_modeler_page", 
            os.path.join(os.path.dirname(__file__), 'streamlit_app', 'pages', '3_DES_Modeler.py')
        )
        des_modeler_page = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(des_modeler_page)
        print("✅ DES Modeler page imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_erlang_calculator_page_import():
    """Test that the Erlang Calculator page can be imported without errors"""
    try:
        # Test importing the Erlang Calculator page
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "erlang_calculator_page", 
            os.path.join(os.path.dirname(__file__), 'streamlit_app', 'pages', '4_Erlang_Calculator.py')
        )
        erlang_calculator_page = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(erlang_calculator_page)
        print("✅ Erlang Calculator page imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("Testing DES Modeler and Erlang Calculator components...")
    print("=" * 60)
    
    success = True
    
    # Test imports
    success &= test_simulation_model_import()
    success &= test_des_modeler_page_import()
    success &= test_erlang_calculator_page_import()
    
    print("=" * 60)
    if success:
        print("✅ All tests passed! The DES Modeler and Erlang Calculator should work correctly.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    print("\nTo run the Streamlit app:")
    print("cd v0_6_0")
    print("streamlit run streamlit_app/app.py") 