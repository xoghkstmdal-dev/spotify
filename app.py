import streamlit as st
import pandas as pd
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# =========================================================
# Spotify 연결 (Streamlit Secrets)
# =========================================================
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]

auth_manager = SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)
sp = spotipy.Spotify(auth_manager=auth_manager)


# =========================================================
# 유틸 함수
# =========================================================
def search_tracks(query: str):
    res = sp.search(q=query, type="track", limit=10)
    items = res["tracks"]["items"]
    return [
        {
            "title": i["name"],
            "artist": i["artists"][0]["name"],
            "id": i["id"]
        }
        for i in items
    ]


def spotify_recommend(seed_ids, limit=20):
    # ★ 핵심 수정: seed_ids 리스트 그대로 전달해야 API 404 안 뜬다
    rec = sp.recommendations(seed_tracks=seed_ids, limit=limit)
    return rec["tracks"]


# =========================================================
# Streamlit UI
# =========================================================
st.set_page_config(page_title="Mini Music Curator", layout="wide")

st.title("🎧 Mini Music Curator (Spotify 기반 추천)")

st.write("검색어 → 씨드곡 선택 → 추천 생성\n")

col1, col2, col3 = st.columns(3)

with col1:
    q1 = st.text_input("검색어 1", "")
    result1 = search_tracks(q1) if q1 else []
    pick1 = st.selectbox("씨드곡 선택", ["(선택 안 함)"] + [f"{x['title']} - {x['artist']}" for x in result1])
    id1 = None
    if pick1 != "(선택 안 함)":
        id1 = result1[[f"{x['title']} - {x['artist']}" for x in result1].index(pick1)]["id"]

with col2:
    q2 = st.text_input("검색어 2", "")
    result2 = search_tracks(q2) if q2 else []
    pick2 = st.selectbox("씨드곡 선택 ", ["(선택 안 함)"] + [f"{x['title']} - {x['artist']}" for x in result2])
    id2 = None
    if pick2 != "(선택 안 함)":
        id2 = result2[[f"{x['title']} - {x['artist']}" for x in result2].index(pick2)]["id"]

with col3:
    q3 = st.text_input("검색어 3", "")
    result3 = search_tracks(q3) if q3 else []
    pick3 = st.selectbox("씨드곡 선택  ", ["(선택 안 함)"] + [f"{x['title']} - {x['artist']}" for x in result3])
    id3 = None
    if pick3 != "(선택 안 함)":
        id3 = result3[[f"{x['title']} - {x['artist']}" for x in result3].index(pick3)]["id"]

# 추천 개수 설정
limit = st.slider("추천 곡 수", 5, 50, 15)

# 실행 버튼
if st.button("Spotify 추천 생성"):
    seed_ids = [x for x in [id1, id2, id3] if x]

    if len(seed_ids) == 0:
        st.error("최소 1개의 씨드곡을 선택하세요.")
    else:
        try:
            tracks = spotify_recommend(seed_ids, limit=limit)

            if len(tracks) == 0:
                st.warning("추천 결과가 없습니다.")
            else:
                df = pd.DataFrame([
                    {
                        "title": t["name"],
                        "artist": t["artists"][0]["name"],
                        "album": t["album"]["name"],
                        "preview": t.get("preview_url", None),
                        "spotify": t["external_urls"]["spotify"]
                    }
                    for t in tracks
                ])
                st.success("추천 생성 완료!")
                st.dataframe(df)

                for idx, row in df.iterrows():
                    st.markdown(
                        f"🎵 **{row['title']}** — {row['artist']}  "
                        f"[Spotify 링크]({row['spotify']})"
                    )

        except Exception as e:
            st.error(f"오류 발생: {e}")
