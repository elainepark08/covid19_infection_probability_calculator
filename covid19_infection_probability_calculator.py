import streamlit as st
import numpy as np
from scipy.integrate import odeint

# SEIR 모델 함수 정의
def seir_model(y, t, N, beta, sigma, gamma):
    S, E, I, R = y
    dSdt = -beta * S * I / N
    dEdt = beta * S * I / N - sigma * E
    dIdt = sigma * E - gamma * I
    dRdt = gamma * I
    return [dSdt, dEdt, dIdt, dRdt]

# 감염 확률 계산 함수
def calculate_infection_probability(age, vaccinated, vaccine_type, dose_count, previously_infected_count):
    base_beta = 0.3

    # 나이대에 따른 감염률 조정
    if age >= 60:
        beta = base_beta * 1.2
    elif age <= 18:
        beta = base_beta * 0.8
    else:
        beta = base_beta

    # 백신 종류에 따른 감염률 감소 조정
    if vaccinated:
        if vaccine_type == "화이자":
            beta *= 0.6 if dose_count >= 2 else 0.75
        elif vaccine_type == "모더나":
            beta *= 0.5 if dose_count >= 2 else 0.7
        elif vaccine_type == "AZ":
            beta *= 0.65 if dose_count >= 2 else 0.8

    # 이전 감염 횟수에 따른 감염률 조정
    if previously_infected_count == 1:
        beta *= 0.7
    elif previously_infected_count >= 2:
        beta *= 0.5

    N = 10000
    sigma = 1/5.2
    gamma = 1/14
    S0, E0, I0, R0 = N - 1, 1, 0, 0
    initial_state = [S0, E0, I0, R0]
    t = np.linspace(0, 160, 160)

    result = odeint(seir_model, initial_state, t, args=(N, beta, sigma, gamma))
    S, E, I, R = result.T

    final_infected_ratio = I[-1] / N
    infection_probability = min(final_infected_ratio * 100, 100)

    return infection_probability

# Streamlit 앱 UI
st.title("코로나 바이러스 감염 확률 예측")
st.write("사용자의 연령, 백신 접종 여부, 백신 종류, 접종 횟수, 이전 감염 여부를 기반으로 감염 확률을 예측합니다.")

# 사용자 입력
age = st.slider("연령대", 0, 100, 30)
vaccinated = st.selectbox("백신 접종 여부", ["미접종", "접종 완료"])
if vaccinated == "접종 완료":
    vaccine_type = st.selectbox("백신 종류", ["화이자", "모더나", "AZ"])
    dose_count = st.selectbox("접종 횟수", ["1차", "2차", "3차 이상"])

previously_infected_count = st.selectbox("이전 감염 횟수", ["감염되지 않음", "1회 감염", "2회 이상 감염"])

# 감염 확률 계산 버튼 클릭 시
if st.button("감염 확률 계산"):
    probability = calculate_infection_probability(
        age, 
        vaccinated == "접종 완료", 
        vaccine_type,         
        dose_count,           
        previously_infected_count  
    )
    st.write(f"코로나 바이러스에 감염될 확률은 {probability:.2f}%입니다.")

