from app.graph.graph import run_pipeline


def test_run_pipeline_preserves_thread_id():
    state = run_pipeline('Studio close to transit', thread_id='session-abc-123')
    assert state['thread_id'] == 'session-abc-123'
    assert state['user_query'] == 'Studio close to transit'
    assert 'intent' in state
    assert 'scored' in state
