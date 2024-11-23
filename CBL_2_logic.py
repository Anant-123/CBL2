import streamlit as st
import numpy as np
import pandas as pd

def recovery(w, b, angle_deg, disc_to_border, disc_to_disc):
    # Convert angle from degrees to radians
    angle_rad = np.pi * angle_deg / 180
    t = 1
    blank_center = b + disc_to_disc
    tool_pitch = blank_center * np.sin(angle_rad)
    coil_pitch = blank_center * np.cos(angle_rad)
    
    # Usable width
    usable_width = w - 2 * disc_to_border
    
    # Ensure that the usable width is positive
    if usable_width <= b:
        return -np.inf  # Infeasible solution
    
    # Number of blanks
    no_of_blanks = np.floor((usable_width - b) / tool_pitch) + 1
    
    # Material used
    material_used = 2 * coil_pitch * w * t / 1000  # in cubic meters
    
    # Blank volume
    blank_vol = (no_of_blanks * np.pi * b**2 * t) / 4000  # in cubic meters
    
    # Percentage loss
    percent_loss = (material_used - blank_vol) / material_used * 100
    
    # Percentage recovery
    percent_recovery = 100 - percent_loss
    
    return percent_recovery

# Streamlit app

st.title("CBL-2 Optimal Recovery Calculator")

# Input from user
width = st.number_input("Enter the width of the coil (w) in mm:", min_value=865, value=1320, step=10)
diameter = st.number_input("Enter the diameter of the blanks (b) in mm:", min_value=100, value=250, step=1)

# Allow user to set ranges for iteration dynamically
st.sidebar.header("Set Iteration Ranges")
disc_to_disc_range = st.sidebar.slider(
    "Select range for Disc to Disc (mm):",
    min_value=1, max_value=20, value=(8, 10), step=1
)
disc_to_border_range = st.sidebar.slider(
    "Select range for Disc to Border (mm):",
    min_value=10, max_value=50, value=(30, 40), step=1
)

# Generate the ranges
disc_to_disc_values = range(disc_to_disc_range[0], disc_to_disc_range[1] + 1)
disc_to_border_values = range(disc_to_border_range[0], disc_to_border_range[1] + 1)

# Button to calculate
if st.button("Calculate Optimal Values"):
    # Fixed angle range
    angle_values = np.arange(30, 60.1, 1.5)  # Vary Angle from 30 to 60 degrees in steps of 1.5
    
    results = []
    
    # Iterate over all combinations
    for disc_to_disc in disc_to_disc_values:
        for disc_to_border in disc_to_border_values:
            for angle_deg in angle_values:
                recovery_value = recovery(width, diameter, angle_deg, disc_to_border, disc_to_disc)
                if recovery_value > 0:  # Only feasible solutions
                    results.append({
                        "Disc to Disc (mm)": disc_to_disc,
                        "Disc to Border (mm)": disc_to_border,
                        "Angle (deg)": angle_deg,
                        "Recovery (%)": recovery_value
                    })

    if results:
        df = pd.DataFrame(results)
        optimal_row = df.loc[df["Recovery (%)"].idxmax()]
        
        # Styled Result Box
        st.markdown(
            f"""
            <div style="
                background-color: #d3d9e7; 
                border-radius: 10px; 
                padding: 20px; 
                margin: 10px 0px;
                box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
            ">
                <h3 style="color: #333333;">Optimal Recovery Results 🔍</h3>
                <ul style="color: #444444; font-size: 18px; line-height: 1.6;">
                    <li><strong>Disc to Disc:</strong> {optimal_row['Disc to Disc (mm)']} mm</li>
                    <li><strong>Disc to Border:</strong> {optimal_row['Disc to Border (mm)']} mm</li>
                    <li><strong>Angle:</strong> {optimal_row['Angle (deg)']:.1f} degrees</li>
                    <li><strong>Maximum Recovery:</strong> {optimal_row['Recovery (%)']:.2f} %</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("### Full Results Table")
        st.dataframe(df.sort_values(by="Recovery (%)", ascending=False))
    else:
        st.write("No feasible solutions found. Please adjust your inputs.")

