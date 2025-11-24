import streamlit as st
import pandas as pd
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


# ───────────────────────────────────────────────────────────────
# 🎧 Spotify API 로그인 없이 사용 (Client Credentials 방식)
# ───────────────────────────────────────────────────────────────
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]

auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)


# ───────────────────────────────────────────────────────────────
# 📌 Spotify 검색 함수
# ───────────────────────────────────────────────────────────────
def spotify_search_tracks(query: str, limit: int = 10):
    res = sp.search(q=query, type="track", limit=limit)
    tracks = []

    for item in res["tracks"]["items"]:
        tracks.append({
            "title": item["name"],
            "artist": item["artists"][0]["name"],
            "id": item["id"]
        })

    return pd.DataFrame(tracks)


# ───────────────────────────────────────────────────────────────
# 📌 Spotify 추천 함수 (핵심)
# ───────────────────────────────────────────────────────────────
# seed_ids 는 "ID 문자열의 리스트" 그대로 전달해야 한다!!!!  (join 절대 X)
def spotify_recommend(sp: spotipy.Spotify, seed_ids: list[str], limit: int = 50):
    rec = sp.recommendations(seed_tracks=seed_ids, limit=limit)
    return rec["tracks"]


# ───────────────────────────────────────────────────────────────
# 🎨 Streamlit UI
# ───────────────────────────────────────────────────────────────
st.title("🎧 Mini Music Curator (Prototype)")
st.write("3곡을 선택하고, 큐레이션 컨셉을 선택하면\n데이터 기반 또는 Spotify 기반으로 비슷한 무드/장르/날씨의 곡을 추천해주는 앱입니다.")

tab1, tab2 = st.tabs(["📂 더미 데이터 모드", "🎵 Spotify 모드"])


# ───────────────────────────────────────────────────────────────
# 📂 TAB 2 — Spotify 기반 추천 모드
# ───────────────────────────────────────────────────────────────
with tab2:
    st.header("Spotify 기반 추천 (로그인 없이)")
    st.write("각 칸에 검색어를 입력하고, 결과에서 씨드 곡을 골라주세요 (최대 3곡).")

    col1, col2, col3 = st.columns(3)

    with col1:
        q1 = st.text_input("검색어 1", "")
        df1 = spotify_search_tracks(q1) if q1 else pd.DataFrame()
        s1 = st.selectbox("씨드 곡 선택", df1["title"] + " – " + df1["artist"] if not df1.empty else [], index=None)

    with col2:
        q2 = st.text_input("검색어 2", "")
        df2 = spotify_search_tracks(q2) if q2 else pd.DataFrame()
        s2 = st.selectbox("씨드 곡 선택", df2["title"] + " – " + df2["artist"] if not df2.empty else [], index=None)

    with col3:
        q3 = st.text_input("검색어 3", "")
        df3 = spotify_search_tracks(q3) if q3 else pd.DataFrame()
        s3 = st.selectbox("씨드 곡 선택", df3["title"] + " – " + df3["artist"] if not df3.empty else [], index=None)

    seed_candidates = []
    if s1 and not df1.empty: seed_candidates.append(df1.loc[df1["title"] + " – " + df1["artist"] == s1]["id"].iloc[0])
    if s2 and not df2.empty: seed_candidates.append(df2.loc[df2["title"] + " – " + df2["artist"] == s2]["id"].iloc[0])
    if s3 and not df3.empty: seed_candidates.append(df3.loc[df3["title"] + " – " + df3["artist"] == s3]["id"].iloc[0])

    curate_mode = st.radio("🔎 큐레이션 컨셉 (Spotify)", ["기본 추천", "유명하지 않은 곡"])
    rec_count = st.slider("추천 곡 수", 5, 30, 15)

    if st.button("Spotify 추천 생성"):
        if len(seed_candidates) == 0:
            st.warning("적어도 한 곡을 선택해야 합니다.")
        else:
            try:
                cand_tracks = spotify_recommend(sp, seed_candidates, limit=rec_count)
                df_res = pd.DataFrame([
                    {
                        "title": t["name"],
                        "artist": t["artists"][0]["name"],
                        "popularity": t["popularity"],
                        "preview": t["preview_url"],
                        "spotify": t["external_urls"]["spotify"]
                    }
                    for t in cand_tracks
                ])

                # 유명하지 않은 곡 옵션 적용
                if curate_mode == "유명하지 않은 곡":
                    df_res = df_res[df_res["popularity"] < 50].reset_index(drop=True)

                st.subheader("추천 결과")
                st.dataframe(df_res[["title", "artist", "popularity"]], hide_index=True)

                for _, r in df_res.iterrows():
                    st.markdown(f"🎵 [{r['title']} – {r['artist']}]({r['spotify']})")

            except Exception as e:
                st.error(str(e))


# ───────────────────────────────────────────────────────────────
# 🔚 END
# ───────────────────────────────────────────────────────────────
