"""Halaman Manajemen Konten Website (CMS) untuk Administrator ARUNA.

Menyediakan antarmuka CRUD (Create, Read, Update, Delete) untuk:
1. Pengumuman & Informasi Kampus.
2. Kontak Bantuan & Konseling Darurat.
3. FAQ Edukasi Kesehatan Mental.
"""

from __future__ import annotations
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd

from src.theme import apply_theme, get_vector, get_logo_base64
from src.database import (
    initialize_database,
    get_announcements,
    add_announcement,
    update_announcement,
    delete_announcement,
    get_support_contacts,
    add_support_contact,
    update_support_contact,
    delete_support_contact,
    get_faqs,
    add_faq,
    update_faq,
    delete_faq,
)

# Cek autentikasi dan peran admin
current_user = st.session_state.get("user")
is_admin = bool(current_user and current_user.get("role") == "admin")

# Terapkan styling & kontrol visibilitas sidebar
apply_theme(hide_sidebar=not is_admin)

if not is_admin:
    st.warning("⚠️ Akses Terbatas: Halaman ini hanya dapat diakses oleh Administrator.")
    st.info("Silakan login menggunakan akun Administrator di Beranda Utama.")
    st.page_link("pages/0_Home.py", label="⬅️ Kembali ke Beranda Utama", icon="🌱")
    st.stop()

# Tombol navigasi kembali ke Admin Dashboard
st.page_link("pages/1_Admin_Dashboard.py", label="⬅️ Kembali ke Admin Dashboard", icon="🏠")

initialize_database()

# Header Halaman
logo_data_uri = get_logo_base64()
h_col1, h_col2 = st.columns([3, 1], vertical_alignment="center")
with h_col1:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 8px;">
            <img src="{logo_data_uri}" alt="Aruna Logo" style="width: 44px; height: 44px; object-fit: contain;" />
            <div>
                <span class="aruna-badge">Administrator CMS</span>
                <h1 class="aruna-brand-title" style="margin: 0; font-size: 2.1rem;">Aruna</h1>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.title("Manajemen Konten Website")
    st.caption("Kelola pengumuman, daftar kontak bantuan, dan FAQ kesehatan mental yang tampil di portal mahasiswa.")

with h_col2:
    st.markdown(f'<div style="max-width: 120px; margin: auto;">{get_vector("research_matrix")}</div>', unsafe_allow_html=True)

st.divider()

# Tab Navigasi CRUD
tab_announcement, tab_contacts, tab_faqs = st.tabs([
    "📢 Pengumuman Kampus",
    "📞 Kontak Bantuan & Konseling",
    "❓ FAQ Edukasi",
])


# ===========================================================================
# 1. CRUD PENGUMUMAN
# ===========================================================================
with tab_announcement:
    st.subheader("Pengumuman & Berita Kampus")

    # Form Tambah Pengumuman Baru
    with st.expander("➕ Tambah Pengumuman Baru", expanded=False):
        with st.form("form_add_announcement"):
            new_title = st.text_input("Judul Pengumuman:")
            new_content = st.text_area("Isi Pengumuman / Pesan Edukasi:")
            new_status = st.checkbox("Langsung Terbitkan (Aktif)", value=True)
            submit_add_ann = st.form_submit_button("Simpan Pengumuman", type="primary")

            if submit_add_ann:
                if not new_title.strip() or not new_content.strip():
                    st.error("Judul dan isi pengumuman tidak boleh kosong.")
                else:
                    add_announcement(new_title, new_content, new_status)
                    st.success("Pengumuman berhasil ditambahkan!")
                    st.rerun()

    # Daftar Pengumuman Eksisting
    announcements = get_announcements(active_only=False)

    if not announcements:
        st.info("Belum ada pengumuman yang dibuat.")
    else:
        for ann in announcements:
            with st.container():
                st.markdown(
                    f"""
                    <div class="aruna-card" style="margin-bottom: 12px; padding: 20px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h4 style="margin: 0; color: var(--aruna-text-main);">{ann['title']}</h4>
                            <span class="aruna-badge">{'🟢 Aktif' if ann['is_active'] else '⚪ Arsip'}</span>
                        </div>
                        <p style="color: var(--aruna-text-sub); margin: 10px 0; font-size: 0.95rem;">{ann['content']}</p>
                        <div style="font-size: 0.8rem; color: var(--aruna-text-sub);">Dibuat: {ann['created_at']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                col_btn1, col_btn2 = st.columns([1, 1])
                with col_btn1:
                    with st.popover(f"✏️ Edit #{ann['id']}"):
                        with st.form(f"edit_ann_{ann['id']}"):
                            edit_title = st.text_input("Judul:", value=ann["title"])
                            edit_content = st.text_area("Isi:", value=ann["content"])
                            edit_active = st.checkbox("Aktif:", value=bool(ann["is_active"]))
                            if st.form_submit_button("Simpan Perubahan"):
                                update_announcement(ann["id"], edit_title, edit_content, edit_active)
                                st.success("Diperbarui!")
                                st.rerun()

                with col_btn2:
                    if st.button(f"🗑️ Hapus #{ann['id']}", key=f"del_ann_{ann['id']}", type="secondary"):
                        delete_announcement(ann["id"])
                        st.warning("Pengumuman dihapus!")
                        st.rerun()


# ===========================================================================
# 2. CRUD KONTAK BANTUAN & KONSELING
# ===========================================================================
with tab_contacts:
    st.subheader("Kontak Konseling & Layanan Krisis Mahasiswa")

    with st.expander("➕ Tambah Kontak Bantuan Baru", expanded=False):
        with st.form("form_add_contact"):
            c_name = st.text_input("Nama Lembaga / Layanan:")
            c_category = st.selectbox("Kategori Layanan:", ["Konseling Kampus", "Layanan Nasional", "Layanan Darurat", "Komunitas Sebaya"])
            c_phone = st.text_input("Nomor Telepon / WhatsApp / Hotline:")
            c_desc = st.text_area("Deskripsi Layanan & Jadwal Operasional:")
            c_active = st.checkbox("Status Aktif", value=True)
            submit_add_c = st.form_submit_button("Simpan Kontak", type="primary")

            if submit_add_c:
                if not c_name.strip() or not c_phone.strip():
                    st.error("Nama lembaga dan nomor kontak wajib diisi.")
                else:
                    add_support_contact(c_name, c_category, c_phone, c_desc, c_active)
                    st.success("Kontak bantuan berhasil ditambahkan!")
                    st.rerun()

    contacts = get_support_contacts(active_only=False)
    if not contacts:
        st.info("Belum ada kontak bantuan yang terdaftar.")
    else:
        for c in contacts:
            st.markdown(
                f"""
                <div class="aruna-card" style="padding: 18px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; color: var(--aruna-text-main);">{c['name']} ({c['category']})</h4>
                        <span class="aruna-badge">{'🟢 Aktif' if c['is_active'] else '⚪ Nonaktif'}</span>
                    </div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: var(--aruna-accent); margin: 6px 0;">📞 {c['phone']}</div>
                    <p style="color: var(--aruna-text-sub); margin: 0; font-size: 0.9rem;">{c['description']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            col_c1, col_c2 = st.columns([1, 1])
            with col_c1:
                with st.popover(f"✏️ Edit #{c['id']}"):
                    with st.form(f"edit_c_{c['id']}"):
                        ed_name = st.text_input("Nama:", value=c["name"])
                        ed_cat = st.text_input("Kategori:", value=c["category"])
                        ed_phone = st.text_input("Telepon:", value=c["phone"])
                        ed_desc = st.text_area("Deskripsi:", value=c["description"])
                        ed_act = st.checkbox("Aktif:", value=bool(c["is_active"]))
                        if st.form_submit_button("Simpan Kontak"):
                            update_support_contact(c["id"], ed_name, ed_cat, ed_phone, ed_desc, ed_act)
                            st.success("Kontak diperbarui!")
                            st.rerun()
            with col_c2:
                if st.button(f"🗑️ Hapus #{c['id']}", key=f"del_c_{c['id']}"):
                    delete_support_contact(c["id"])
                    st.warning("Kontak dihapus!")
                    st.rerun()


# ===========================================================================
# 3. CRUD FAQ EDUKASI KESEHATAN MENTAL
# ===========================================================================
with tab_faqs:
    st.subheader("FAQ & Pusat Edukasi Mahasiswa")

    with st.expander("➕ Tambah FAQ Baru", expanded=False):
        with st.form("form_add_faq"):
            f_q = st.text_input("Pertanyaan (Question):")
            f_a = st.text_area("Jawaban Edukatif (Answer):")
            f_cat = st.selectbox("Kategori FAQ:", ["Umum", "Privasi & Etika", "Metodologi ML", "Bantuan & Dukungan"])
            f_active = st.checkbox("Status Ditampilkan", value=True)
            submit_faq = st.form_submit_button("Simpan FAQ", type="primary")

            if submit_faq:
                if not f_q.strip() or not f_a.strip():
                    st.error("Pertanyaan dan jawaban wajib diisi.")
                else:
                    add_faq(f_q, f_a, f_cat, f_active)
                    st.success("FAQ berhasil ditambahkan!")
                    st.rerun()

    faqs = get_faqs(active_only=False)
    if not faqs:
        st.info("Belum ada FAQ yang dibuat.")
    else:
        for item in faqs:
            with st.expander(f"[{item['category']}] {item['question']}"):
                st.write(item["answer"])
                col_f1, col_f2 = st.columns([1, 1])
                with col_f1:
                    with st.popover(f"✏️ Edit FAQ #{item['id']}"):
                        with st.form(f"edit_f_{item['id']}"):
                            ef_q = st.text_input("Pertanyaan:", value=item["question"])
                            ef_a = st.text_area("Jawaban:", value=item["answer"])
                            ef_cat = st.text_input("Kategori:", value=item["category"])
                            ef_act = st.checkbox("Aktif:", value=bool(item["is_active"]))
                            if st.form_submit_button("Simpan Perubahan FAQ"):
                                update_faq(item["id"], ef_q, ef_a, ef_cat, ef_act)
                                st.success("FAQ diperbarui!")
                                st.rerun()
                with col_f2:
                    if st.button(f"🗑️ Hapus FAQ #{item['id']}", key=f"del_f_{item['id']}"):
                        delete_faq(item["id"])
                        st.warning("FAQ dihapus!")
                        st.rerun()
