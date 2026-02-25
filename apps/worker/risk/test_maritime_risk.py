from maritime_risk_manager import MaritimeRiskManager
import os
import shutil

def test_integration():
    print("Testing Maritime Risk Manager Integration...")
    
    # Use a temp directory for testing
    test_dir = "./test_maritime_data"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    
    manager = MaritimeRiskManager(storage_dir=test_dir)
    
    # 1. Test Lazy Loading (Initially empty)
    print("Checking lazy loading...")
    assert manager._piracy_data is None
    
    # Access property should trigger load/download
    print(f"Piracy data count: {len(manager.piracy_data)}")
    assert manager._piracy_data is not None
    assert len(manager.piracy_data) > 0
    print("✓ Lazy loading works")
    
    # 2. Test Route Assessment
    print("Testing route assessment...")
    route = [
        {"name": "Singapore", "latitude": 1.29, "longitude": 103.85},
        {"name": "Malacca Strait", "latitude": 1.43, "longitude": 103.0},
        {"name": "Suez Canal", "latitude": 30.52, "longitude": 32.34}
    ]
    
    assessment = manager.assess_route_risk(route)
    print(f"Overall Risk Score: {assessment['overall_risk_score']}")
    print(f"Risk Level: {assessment['risk_level']}")
    
    assert assessment['overall_risk_score'] >= 0
    print("✓ Route assessment works")
    
    # 3. Test Memory Clear
    print("Testing memory clearing...")
    manager.clear_memory()
    assert manager._piracy_data is None
    print("✓ Memory clear works")
    
    # Cleanup
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    
    print("\n✓ ALL TESTS PASSED")

if __name__ == "__main__":
    test_integration()
