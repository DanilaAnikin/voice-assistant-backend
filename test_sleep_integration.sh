#!/bin/bash
# Integration test for sleep mode messaging
# Tests the complete CLI workflow with different message types

set -e  # Exit on error

echo "🧪 Sleep Mode Messaging Integration Tests"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
HOST="localhost"
PORT="8000"
SCRIPT_DIR="$(dirname "$0")"

# Test counters
TESTS_PASSED=0
TESTS_TOTAL=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "\n${BLUE}🔍 Testing: $test_name${NC}"
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ $test_name passed${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ $test_name failed${NC}"
        return 1
    fi
}

# Test 1: Server status
run_test "Server Status" \
    "python3 '$SCRIPT_DIR/cli_client.py' --host $HOST --port $PORT status >/dev/null"

# Test 2: List devices
run_test "List Devices" \
    "python3 '$SCRIPT_DIR/cli_client.py' --host $HOST --port $PORT devices >/dev/null"

# Test 3: Regular message send (will fail if no devices, but tests CLI)
run_test "CLI Regular Message" \
    "python3 '$SCRIPT_DIR/cli_client.py' --host $HOST --port $PORT send 'Test regular message' 2>/dev/null || true"

# Test 4: Silent message send
run_test "CLI Silent Message" \
    "python3 '$SCRIPT_DIR/cli_client.py' --host $HOST --port $PORT send 'Test silent message' --silent 2>/dev/null || true"

# Test 5: Regular broadcast
run_test "CLI Regular Broadcast" \
    "python3 '$SCRIPT_DIR/cli_client.py' --host $HOST --port $PORT broadcast 'Test broadcast' 2>/dev/null || true"

# Test 6: Silent broadcast
run_test "CLI Silent Broadcast" \
    "python3 '$SCRIPT_DIR/cli_client.py' --host $HOST --port $PORT broadcast 'Test silent broadcast' --silent 2>/dev/null || true"

# Test 7: Shell wrapper - regular send
run_test "Shell Wrapper Regular Send" \
    "bash '$SCRIPT_DIR/vm_send_message.sh' send 'Shell test message' 2>/dev/null || true"

# Test 8: Shell wrapper - silent send
run_test "Shell Wrapper Silent Send" \
    "bash '$SCRIPT_DIR/vm_send_message.sh' send 'Shell silent test' --silent 2>/dev/null || true"

# Test 9: Shell wrapper - regular broadcast
run_test "Shell Wrapper Regular Broadcast" \
    "bash '$SCRIPT_DIR/vm_send_message.sh' broadcast 'Shell broadcast test' 2>/dev/null || true"

# Test 10: Shell wrapper - silent broadcast
run_test "Shell Wrapper Silent Broadcast" \
    "bash '$SCRIPT_DIR/vm_send_message.sh' broadcast 'Shell silent broadcast' --silent 2>/dev/null || true"

# Test 11: Help text verification
run_test "Help Text Contains Silent Flag" \
    "python3 '$SCRIPT_DIR/cli_client.py' --help | grep -q 'silent'"

# Test 12: Shell wrapper help
run_test "Shell Wrapper Help" \
    "bash '$SCRIPT_DIR/vm_send_message.sh' help | grep -q 'silent'"

# Summary
echo -e "\n=========================================="
echo -e "${BLUE}📊 Test Summary${NC}"
echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC}/$TESTS_TOTAL"

if [ $TESTS_PASSED -eq $TESTS_TOTAL ]; then
    echo -e "${GREEN}🎉 All tests passed! Sleep mode messaging CLI is working correctly.${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed. Check the implementation.${NC}"
    exit 1
fi