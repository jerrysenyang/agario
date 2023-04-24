import pytest
from testfixtures import compare
from collections import deque

from replication import ViewServer, Node
import proto.replica_pb2 as replica


@pytest.fixture
def node():
    return Node("0", "localhost", "5001")


# def test_append_custom_queue():
#     queue = CustomQueue(max_size=10)
#     queue.append(2)
    
#     assert len(queue) == 1
#     assert queue.pop() == 2


def test_vs_current_view_empty():
    vs = ViewServer()
    actual = vs._current_view()
    expected = replica.ViewState(view_id=0)
    compare(actual, expected)


def test_vs_current_view():
    vs = ViewServer()
    vs.primary_id = "3"
    vs.backup_id = "5"
    actual = vs._current_view()
    expected = replica.ViewState(view_id=0, primary_id="3", backup_id="5")

    compare(actual, expected)


def test_check_active_connections_no_backup(node):
    vs = ViewServer()
    backup_node = Node("1", "localhost", "5002")
    vs.nodes = {"0": node, "1": backup_node} 
    vs.primary_id = "0"
    vs.backup_id = "1"
    # Simulate only backup pinging
    vs.recent_pings = deque(["1", "1", "1","1"], maxlen=4)
    vs._check_active_connections()
    expected_nodes_dict = {"1": backup_node}

    assert vs.primary_id == "1"
    assert vs.backup_id == None
    compare(expected_nodes_dict, vs.nodes)


def test_check_active_connections_new_backup(node):
    vs = ViewServer()
    backup_node = Node("1", "localhost", "5002")
    vs.nodes = {"0": node, "1": backup_node} 
    vs.primary_id = "0"
    vs.backup_id = "1"
    # Simulate only backup pinging
    vs.recent_pings = deque(["1", "1", "1","1"], maxlen=4)
    vs._check_active_connections()
    expected_nodes_dict = {"1": backup_node}

    assert vs.primary_id == "1"
    assert vs.backup_id == None
    compare(expected_nodes_dict, vs.nodes)