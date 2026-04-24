import streamlit as st
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

st.title("모터 프로파일 분석기")

# 데이터 입력
input_text = st.text_area("데이터 붙여넣기 (세로 입력 가능):", height=150)

if input_text:
    try:
        data = [float(x) for x in input_text.split()]
        dist, vs, vst, v1, vmax, a1, amax, d1, dmax = data
        
        # [계산 로직]
        t1, t2 = (v1 - vs) / a1, (vmax - v1) / amax
        t3, t4 = (vmax - v1) / dmax, (v1 - vst) / d1
        t_const = max(0, (dist - (((vs+v1)/2)*t1 + ((v1+vmax)/2)*t2 + ((vmax+v1)/2)*t3 + ((v1+vst)/2)*t4)) / vmax)
        t_arr = [0, t1, t1+t2, t1+t2+t_const, t1+t2+t_const+t3, t1+t2+t_const+t4+t3]
        v_arr = [vs, v1, vmax, vmax, v1, vst]

        # 인터랙티브 그래프 생성
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=t_arr, y=v_arr, mode='lines+markers', name='Velocity', 
                                 marker=dict(size=12, color='blue')))
        fig.update_layout(title="그래프의 점을 마우스로 클릭하세요", clickmode='event')

        # 마커 포인트 체크 시 클릭 이벤트 활성화
        if st.checkbox("Enable Marker Points"):
            # 클릭 이벤트 감지
            selected_points = plotly_events(fig, click_event=True, select_event=False)
            
            # 선택된 포인트 관리 (세션 상태 활용)
            if 'pt_a' not in st.session_state: st.session_state.pt_a = None
            if 'pt_b' not in st.session_state: st.session_state.pt_b = None

            if selected_points:
                point = selected_points[0]
                # A포인트가 비어있거나, A와 B가 모두 차 있으면 A를 새로 지정
                if st.session_state.pt_a is None or (st.session_state.pt_a and st.session_state.pt_b):
                    st.session_state.pt_a = point
                    st.session_state.pt_b = None
                else:
                    st.session_state.pt_b = point

            # 결과 표시
            col1, col2 = st.columns(2)
            if st.session_state.pt_a:
                col1.success(f"Point A: ({st.session_state.pt_a['x']:.4f}, {st.session_state.pt_a['y']:.2f})")
            if st.session_state.pt_b:
                col2.success(f"Point B: ({st.session_state.pt_b['x']:.4f}, {st.session_state.pt_b['y']:.2f})")
            
            if st.session_state.pt_a and st.session_state.pt_b:
                dt = abs(st.session_state.pt_b['x'] - st.session_state.pt_a['x'])
                dy = abs(st.session_state.pt_b['y'] - st.session_state.pt_a['y'])
                st.warning(f"### 차이값: dt = {dt:.4f} s, dy = {dy:.2f} mm/s")
        else:
            st.plotly_chart(fig)

    except Exception as e:
        st.error(f"데이터 처리 오류: {e}")