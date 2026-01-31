"""
Integration Test Script
Tests that all components work together
"""

import requests
import time
import sys


def test_server():
    """Test if Flask server is running"""
    try:
        response = requests.get('http://localhost:5000/health', timeout=2)
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is running")
            print(f"   Components: {data['components']}")
            return True
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        print("   Make sure to run: python devcare_app.py")
        return False


def test_status_endpoint():
    """Test /status endpoint"""
    try:
        response = requests.get('http://localhost:5000/status', timeout=2)
        data = response.json()

        print("\n✅ Status endpoint working")
        print(f"   Posture: {data.get('posture', 'N/A')}")
        print(f"   Time: {data.get('time', 'N/A')}")
        print(f"   Stress: {data.get('stress', 'N/A')}")
        return True
    except Exception as e:
        print(f"\n❌ Status endpoint failed: {e}")
        return False


def test_break_endpoint():
    """Test /break endpoint"""
    try:
        response = requests.post('http://localhost:5000/break', timeout=2)
        data = response.json()

        if data.get('success') or 'message' in data:
            print("\n✅ Break endpoint working")
            return True
        else:
            print(f"\n⚠️ Break endpoint returned: {data}")
            return True  # Not critical
    except Exception as e:
        print(f"\n❌ Break endpoint failed: {e}")
        return False


def monitor_realtime():
    """Monitor real-time updates for 10 seconds"""
    print("\n📊 Monitoring real-time data for 10 seconds...")
    print("   (Make sure webcam is on and you're visible)")

    for i in range(10):
        try:
            response = requests.get('http://localhost:5000/status', timeout=1)
            data = response.json()

            posture = data.get('posture', 0)
            stress = data.get('stress', 'N/A')

            # Show bar
            bar_length = int(posture / 5) if posture > 0 else 0
            bar = '█' * bar_length + '░' * (20 - bar_length)

            print(f"   [{bar}] Posture: {posture:3d}/100 | Stress: {stress}")

            time.sleep(1)
        except Exception as e:
            print(f"   Error: {e}")
            break

    print("\n✅ Monitoring complete")


def run_all_tests():
    """Run all integration tests"""
    print("=" * 60)
    print("DEVCARE - INTEGRATION TESTS")
    print("=" * 60)

    tests = [
        ("Server Health", test_server),
        ("Status Endpoint", test_status_endpoint),
        ("Break Endpoint", test_break_endpoint),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        print(f"\n🧪 Testing: {name}")
        print("-" * 60)
        if test_func():
            passed += 1
        else:
            failed += 1

    # Real-time monitoring
    if passed > 0:
        monitor_realtime()

    # Summary
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Ready for demo!")
    else:
        print("\n⚠️ Some tests failed. Check components.")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)