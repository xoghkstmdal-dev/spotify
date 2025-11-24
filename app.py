import streamlit as st
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# --------------------------------------------------
# 1. Spotify 인증 (Streamlit Cloud Secrets 사용)
# --------------------------------------------------
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]

auth_manager = SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
)
sp = spotipy.Spotify(auth_manager=auth_manager)


# --------------------------------------------------
# 2. Spotify 유틸 함수
# --------------------------------------------------
def search_tracks(query: str):
    """검색어로 트랙 10개까지 검색해서 (id, label, url) 리스트 반환"""
    if not query.strip():
        return []

    res = sp.search(q=query, type="track", limit=10)
    items = res["tracks"]["items"]

    tracks = []
    for t in items:
        label = f"{t['name']} – {t['artists'][0]['name']}"
        tracks.append(
            {
                "id": t["id"],
                "label": label,
                "name": t["name"],
                "artist": t["artists"][0]["name"],
                "url": t["external_urls"]["spotify"],
            }
        )
    return tracks


def recommend_from_seeds(seed_ids, limit: int = 20):
    """
    seed_ids: ['id1', 'id2', ...] 형태의 리스트
    ★ 중요: 여기서 절대 ','.join(seed_ids) 같은 문자열로 바꾸지 않는다.
    """
    rec = sp.recommendations(seed_tracks=seed_ids, limit=limit)
    tracks = []
    for t in rec["tracks"]:
        tracks.append(
            {
                "name": t["name"],
                "artist": t["artists"][0]["name"],
                "popularity": t["popularity"],
                "url": t["external_urls"]["spotify"],
            }
        )
    return tracks


# --------------------------------------------------
# 3. Streamlit UI
# --------------------------------------------------
st.set_page_config(page_title="Mini Music Curator", layout="wide")

st.title("🎧 Mini Music Curator (Spotify Prototype)")
st.caption("검색어 1~3개 → 씨드 곡 선택 → Spotify 추천 생성")

col1, col2, col3 = st.columns(3)

# ----- 검색/선택 1 -----
with col1:
    q1 = st.text_input("검색어 1", key="q1")
    tracks1 = search_tracks(q1) if q1 else []
    labels1 = ["(선택 안 함)"] + [t["label"] for t in tracks1]
    choice1 = st.selectbox("씨드 곡 선택 1", options=labels1, key="seed1")

# ----- 검색/선택 2 -----
with col2:
    q2 = st.text_input("검색어 2", key="q2")
    tracks2 = search_tracks(q2) if q2 else []
    labels2 = ["(선택 안 함)"] + [t["label"] for t in tracks2]
    choice2 = st.selectbox("씨드 곡 선택 2", options=labels2, key="seed2")

# ----- 검색/선택 3 -----
with col3:
    q3 = st.text_input("검색어 3", key="q3")
    tracks3 = search_tracks(q3) if q3 else []
    labels3 = ["(선택 안 함)"] + [t["label"] for t in tracks3]
    choice3 = st.selectbox("씨드 곡 선택 3", options=labels3, key="seed3")

# 선택된 씨드 ID 모으기
seed_ids = []

if choice1 != "(선택 안 함)":
    idx = labels1.index(choice1) - 1
    seed_ids.append(tracks1[idx]["id"])

if choice2 != "(선택 안 함)":
    idx = labels2.index(choice2) - 1
    seed_ids.append(tracks2[idx]["id"])

if choice3 != "(선택 안 함)":
    idx = labels3.index(choice3) - 1
    seed_ids.append(tracks3[idx]["id"])

# 추천 개수 설정
limit = st.slider("추천 곡 수", min_value=5, max_value=50, value=15, step=5)

# --------------------------------------------------
# 4. 추천 실행 버튼
# --------------------------------------------------
if st.button("Spotify 추천 생성"):
    if not seed_ids:
        st.warning("최소 1곡 이상 씨드 곡을 선택해 줘.")
    else:
        # seed_ids가 어떻게 생겼는지 디버깅용 출력 (Cloud 로그에서 확인 가능)
        st.write("사용된 seed_ids:", seed_ids)

        try:
            rec_tracks = recommend_from_seeds(seed_ids, limit=limit)

            if not rec_tracks:
                st.warning("추천 결과가 비어 있어.")
            else:
                df = pd.DataFrame(rec_tracks)
                st.subheader("추천 결과")
                st.dataframe(df[["name", "artist", "popularity"]], hide_index=True)

                st.markdown("---")
                st.markdown("**Spotify 링크**")
                for row in rec_tracks:
                    st.markdown(f"- [{row['name']} – {row['artist']}]({row['url']})")

        except Exception as e:
            st.error(f"Spotify 호출 중 오류: {e}")
