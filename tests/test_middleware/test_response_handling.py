def test_response_containing_uuid(client):
    """
    Makes sure that a response containing a uuid4 value doesn't throw a SwaggerDocumentationError when checked with
    the middleware.

    A returned uuid4 will be parsed as a string when unpacking a response.json(), but in the middleware,
    this is not the case if you use response.data. We've added logic to correct this difference, and this test is in place
    to make sure we dont break that logic.
    """
    response = client.post('/api/v1/items', data={'itemType': 'bicycle'})
    assert response.json()['success']['itemType'] == 'bicycle'