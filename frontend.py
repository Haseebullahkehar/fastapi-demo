import streamlit as st
import requests

API_URL = "http://54.221.30.182:8000/predict"


st.title("Insurance Premium Category Predictor")
st.markdown("Enter your details below to predict your insurance premium category:")

# Add some styling
st.markdown("""
<style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 16px;
    }
    .stSuccess {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 4px;
        border: 1px solid #c3e6cb;
    }
    .stError {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 4px;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

# Input fields
col1, col2 = st.columns(2)

with col1:
    age = st.number_input("Age", min_value=1, max_value=119, value=30, help="Enter your age in years")
    weight = st.number_input("Weight (kg)", min_value=1.0, value=65.0, help="Enter your weight in kilograms")
    height = st.number_input("Height (m)", min_value=0.5, max_value=2.5, value=1.7, help="Enter your height in meters")
    income_lpa = st.number_input("Annual Income (LPA)", min_value=0.1, value=10.0, help="Annual income in lakhs per annum")

with col2:
    smoker = st.selectbox("Are you a smoker?", options=["Yes", "No"], help="Select whether you smoke or not")
    city = st.text_input("City", value="Mumbai", help="Enter your city name")
    occupation = st.selectbox(
        "Occupation",
        ['retired', 'freelancer', 'student', 'government_job', 'business_owner', 'unemployed', 'private_job'],
        help="Select your occupation"
    )

st.markdown("---")
if st.button("Predict Premium Category", type="primary"):
    input_data = {
        "age": age,
        "weight": weight,
        "height": height,
        "income_lpa": income_lpa,
        "smoker": smoker == "Yes",
        "city": city,
        "occupation": occupation
    }

    try:
        response = requests.post(API_URL, json=input_data, timeout=10)
        result = response.json()

        if response.status_code == 200:
            # Handle nested response structure
            if 'response' in result and isinstance(result['response'], dict):
                prediction_data = result['response']
            else:
                prediction_data = result

            category = prediction_data.get('predicted_category', 'Unknown')
            confidence = prediction_data.get('confidence', 0)
            probabilities = prediction_data.get('class_probabilities', {})

            st.success(f"Predicted Insurance Premium Category: {category}")
            if confidence > 0:
                st.info(f"Confidence: {confidence:.1%}")

            if probabilities:
                st.subheader("Prediction Probabilities:")
                for class_name, prob in probabilities.items():
                    st.write(f"{class_name}: {prob:.1%}")
        else:
            st.error(f"❌ API Error: {response.status_code}")
            if 'detail' in result:
                st.error(f"Details: {result['detail']}")
            else:
                st.write("Response:", result)

    except requests.exceptions.Timeout:
        st.error("❌ Request timed out. The server took too long to respond.")
        st.info("💡 Try again later or check if your AWS server is under heavy load.")
    except requests.exceptions.ConnectionError:
        st.error("❌ Could not connect to the FastAPI server. Make sure it's running on http://54.221.30.182:8000")
        st.info("💡 Your AWS server should be running. Check if the instance is active and the port 8000 is open.")
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Request failed: {str(e)}")
    except ValueError as e:
        st.error(f"❌ Invalid response from server: {str(e)}")
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")