import pytest
from app import app as flask_app  # Importing the Flask app instance
from flask import Flask, request, url_for, redirect, render_template, session, flash
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
import re

@pytest.fixture
def client():
    """
    Create a test client using the Flask application instance.
    """
    with flask_app.test_client() as client:
        yield client

@pytest.mark.parametrize("name, email_or_phone, password, expected_message", [
    ("Another User", "existing@example.com", "password456", b'already in use'),
    ("Invalid User", "invalidemail", "password789", b'Please enter a valid email'),
])
def test_register(client, name, email_or_phone, password, expected_message):
    """
    Test registration with various input data.
    """
    data = {
        'name': name,
        'email_or_phone': email_or_phone,
        'password': password
    }
    response = client.post('/', data=data, follow_redirects=True)
    assert expected_message in response.data
