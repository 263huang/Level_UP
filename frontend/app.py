import streamlit as st

# 假数据
user_info = {
    'avatar': 'https://static.streamlit.io/examples/cat.jpg',
    'name': '张三',
    'level': 5,
    'exp': 3200,
    'next_level_exp': 4000,
    'today_study': '1小时20分',
}

learning_targets = [
    {'title': '操作系统', 'progress': 0.7, 'tags': ['CS基础'], 'update': '2024-06-01'},
    {'title': 'Unity游戏开发', 'progress': 0.3, 'tags': ['开发', '游戏'], 'update': '2024-05-28'},
    {'title': '数据结构', 'progress': 0.9, 'tags': ['算法'], 'update': '2024-05-30'},
    {'title': '深度学习', 'progress': 0.2, 'tags': ['AI'], 'update': '2024-05-25'},
    {'title': 'Web全栈', 'progress': 0.5, 'tags': ['前端', '后端'], 'update': '2024-05-20'},
    {'title': '英语六级', 'progress': 0.6, 'tags': ['语言'], 'update': '2024-05-18'},
]

st.set_page_config(layout="wide", page_title="LevelUP - 个性化知识成长系统")

# === 自定义样式 ===
st.markdown("""
<style>
h2, .title {
    font-family: 'Segoe UI', sans-serif;
}

.nav-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 8px;
    margin-bottom: 0;
}

.nav-logo {
    font-size: 1.6em;
    font-weight: bold;
    color: #1565c0;
}

.nav-avatar img {
    border-radius: 50%;
}

.card {
    background: #fff;
    border-radius: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    padding: 20px;
    margin-bottom: 20px;
}

.card-title {
    font-size: 1.3em;
    font-weight: bold;
    color: #1565c0;
    margin-bottom: 10px;
}

.progress-bar {
    width: 100%;
    height: 12px;
    border-radius: 6px;
    background: #e0e0e0;
    overflow: hidden;
    margin-top: 4px;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(to right, #42a5f5, #66bb6a);
    border-radius: 6px;
}

.tag {
    background-color: #e3f2fd;
    color: #1976d2;
    padding: 2px 8px;
    border-radius: 8px;
    font-size: 0.85em;
    margin-right: 6px;
}

.card-footer {
    margin-top: 12px;
    display: flex;
    gap: 10px;
}

.icon-btn {
    background: none;
    border: none;
    font-size: 1.2em;
    cursor: pointer;
    padding: 4px 6px;
}
</style>
""", unsafe_allow_html=True)

# === 顶部导航栏 ===
st.markdown('<div class="nav-header">', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 5, 1])
with col1:
    st.markdown('<div class="nav-logo">LevelUP 🚀</div>', unsafe_allow_html=True)
with col2:
    st.text_input('搜索', '', placeholder='搜索学习目标、技能点或笔记标题…', label_visibility='collapsed')
with col3:
    st.markdown(f'<div class="nav-avatar"><img src="{user_info["avatar"]}" width="48"></div>', unsafe_allow_html=True)

st.markdown('</div><hr style="margin-top: 8px;">', unsafe_allow_html=True)

# === 主体区域 ===
left_col, right_col = st.columns([1.2, 3.5], gap="large")

# 左栏：个人信息 + 操作按钮
with left_col:
    st.markdown("#### 👤 个人信息")
    st.image(user_info['avatar'], width=80)
    st.markdown(f"**{user_info['name']}**  等级: {user_info['level']}")
    st.progress(user_info['exp'] / user_info['next_level_exp'], text=f"成长值: {user_info['exp']}/{user_info['next_level_exp']}")
    st.markdown(f"📚 今日学习时长: **{user_info['today_study']}**")

    st.markdown("#### ⚡ 快捷操作")
    st.button("➕ 新建学习目标")
    st.button("📝 新建笔记")
    st.button("📥 导入 / 导出")

    st.markdown("#### 📢 推荐 / 公告")
    st.info("📌 今日推荐：复习操作系统第3章")

    st.markdown("#### ⚙️ 设置 / 帮助")
    st.button("设置")
    st.button("帮助")
    st.button("退出登录")

# 右栏：学习目标卡片
with right_col:
    st.markdown("#### 🎯 学习目标")
    for i in range(0, len(learning_targets), 2):
        cols = st.columns(2)
        for j, target in enumerate(learning_targets[i:i+2]):
            with cols[j]:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown(f'<div class="card-title">{target["title"]}</div>', unsafe_allow_html=True)

                # 自定义亮色进度条
                st.markdown(f'''
                    <div class="progress-bar">
                        <div class="progress-fill" style="width:{int(target["progress"] * 100)}%"></div>
                    </div>
                    <div style="font-size:0.85em;color:#555;margin-top:4px;">进度: {int(target["progress"] * 100)}%</div>
                ''', unsafe_allow_html=True)

                # 标签
                tags_html = ''.join([f'<span class="tag">{tag}</span>' for tag in target['tags']])
                st.markdown(f'<div style="margin:8px 0;">{tags_html}</div>', unsafe_allow_html=True)

                # 更新时间
                st.markdown(f"<div style='font-size:0.85em;color:#888;'>🕒 最近更新: {target['update']}</div>", unsafe_allow_html=True)

                # 图标按钮
                st.markdown('''
                    <div class="card-footer">
                        <button class="icon-btn" title="预览">👁️</button>
                        <button class="icon-btn" title="编辑">✏️</button>
                        <button class="icon-btn" title="收藏">⭐</button>
                    </div>
                ''', unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)
