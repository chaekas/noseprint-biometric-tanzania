import os
import requests
import streamlit as st

API_URL = os.getenv("NOSEPRINT_API_URL", "http://127.0.0.1:8000/api/v1")

st.set_page_config(page_title="Nose Print Biometric PoC", page_icon="🐄", layout="wide")
st.title("🐄 Nose Print Biometric Identification")
st.caption("Research proof of concept — a candidate match is not proof of identity.")

page = st.sidebar.radio("Workspace", ["Register animal", "Identify animal", "Animal records"])

if page == "Register animal":
    st.header("Register an animal")
    st.info("Capture 3–5 sharp nose/muzzle images. Use varied angles and consistent lighting.")
    with st.form("register_form"):
        animal_code = st.text_input("Animal code *")
        species = st.selectbox("Species", ["cattle", "goat", "sheep", "other"])
        breed = st.text_input("Breed")
        sex = st.selectbox("Sex", ["unknown", "female", "male"])
        captures = []
        cols = st.columns(3)
        for index in range(5):
            with cols[index % 3]:
                photo = st.camera_input(f"Reference image {index + 1}", key=f"reg_camera_{index}")
                if photo:
                    captures.append((f"image_{index + 1}.jpg", photo.getvalue(), "image/jpeg"))
        submitted = st.form_submit_button("Register animal", type="primary")
    if submitted:
        if not animal_code.strip():
            st.error("Animal code is required.")
        elif len(captures) < 3:
            st.error("Please capture at least 3 images.")
        else:
            try:
                response = requests.post(
                    f"{API_URL}/animals/register",
                    data={"animal_code": animal_code, "species": species, "breed": breed, "sex": sex},
                    files=[("images", item) for item in captures],
                    timeout=180,
                )
                if response.ok:
                    st.success("Animal registered successfully.")
                    st.json(response.json())
                else:
                    st.error(f"API error {response.status_code}: {response.text}")
            except requests.RequestException as exc:
                st.error(f"Could not reach API: {exc}")

elif page == "Identify animal":
    st.header("Scan and identify")
    st.write("Position the nose/muzzle clearly in the frame, then capture one image.")
    photo = st.camera_input("Capture nose print", key="identify_camera")
    if photo and st.button("Identify animal", type="primary"):
        try:
            response = requests.post(
                f"{API_URL}/biometrics/identify",
                files={"image": ("query.jpg", photo.getvalue(), "image/jpeg")},
                timeout=180,
            )
            if response.ok:
                result = response.json()
                if result["decision"] == "candidate":
                    st.success("Potential candidate found — verify manually.")
                    st.subheader(result["candidate"]["animal_code"])
                else:
                    st.warning("Unknown animal: no candidate passed the current threshold.")
                st.json(result)
            else:
                st.error(f"API error {response.status_code}: {response.text}")
        except requests.RequestException as exc:
            st.error(f"Could not reach API: {exc}")

else:
    st.header("Registered animals")
    if st.button("Refresh records"):
        st.rerun()
    try:
        response = requests.get(f"{API_URL}/animals", timeout=30)
        response.raise_for_status()
        rows = response.json()
        if rows:
            st.dataframe(rows, use_container_width=True, hide_index=True)
        else:
            st.info("No animals have been registered yet.")
    except requests.RequestException as exc:
        st.error(f"Could not reach API: {exc}")

st.divider()
st.caption("PoC warning: ResNet18 is an ImageNet-pretrained generic feature extractor, not a validated nose-print biometric model. Validate with animal-disjoint test data before field use.")
