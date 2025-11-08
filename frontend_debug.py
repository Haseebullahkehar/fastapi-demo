# import streamlit as st
# import requests
# import json

# # Use localhost for testing
# # API_URL = "http://127.0.0.1:8000/predict"

# def make_prediction(input_data):
#     """Make a prediction request with detailed error handling"""
#     try:
#         # Show the raw request for debugging
#         st.write("Sending request to:", API_URL)
#         st.write("Request data:", json.dumps(input_data, indent=2))
        
#         # Make the request
#         response = requests.post(API_URL, json=input_data)
        
#         # Show raw response for debugging
#         st.write("Response status code:", response.status_code)
#         st.write("Response headers:", dict(response.headers))
        
#         # Try to get the response text
#         try:
#             st.write("Raw response text:", response.text)
#         except Exception as e:
#             st.write("Could not get response text:", str(e))
        
#         # Parse JSON response
#         result = response.json()
#         return True, result
        
#     except requests.exceptions.ConnectionError as e:
#         return False, f"Connection error: Could not connect to {API_URL}. Is the FastAPI server running?"
#     except json.JSONDecodeError as e:
#         return False, f"Invalid JSON in response: {str(e)}\nRaw response: {response.text}"
#     except Exception as e:
#         return False, f"Unexpected error: {str(e)}"

# # UI Components
# st.title("Insurance Premium Category Predictor (Debug Mode)")
# st.markdown("Enter your details below:")

# # Input fields
# age = st.number_input("Age", min_value=1, max_value=119, value=30)
# weight = st.number_input("Weight (kg)", min_value=1.0, value=65.0)
# height = st.number_input("Height (m)", min_value=0.5, max_value=2.5, value=1.7)
# income_lpa = st.number_input("Annual Income (LPA)", min_value=0.1, value=10.0)
# smoker = st.selectbox("Are you a smoker?", options=[True, False])
# city = st.text_input("City", value="Mumbai")
# occupation = st.selectbox(
#     "Occupation",
#     ['retired', 'freelancer', 'student', 'government_job', 'business_owner', 'unemployed', 'private_job']
# )

# if st.button("Predict Premium Category"):
#     input_data = {
#         "age": age,
#         "weight": weight,
#         "height": height,
#         "income_lpa": income_lpa,
#         "smoker": smoker,
#         "city": city,
#         "occupation": occupation
#     }
    
#     success, result = make_prediction(input_data)
    
#     if success:
#         if isinstance(result, dict) and "predicted_category" in result:
#             st.success(f"Predicted Insurance Premium Category: **{result['predicted_category']}**")
#         else:
#             st.error("Unexpected response format")
#             st.json(result)
#     else:
#         st.error(result)  # Show the error message

# # Debug information in sidebar
# st.sidebar.markdown("""
# ### Debug Information
# - API Endpoint: {}
# - Request Format: POST with JSON body
# """.format(API_URL))

# st.sidebar.markdown("### Expected Response Format")
# st.sidebar.json({
#     "predicted_category": "example_category"
# })