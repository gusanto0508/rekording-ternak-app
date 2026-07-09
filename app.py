# Trigger rebuild

import streamlit as st
import pandas as pd
import numpy as np
from scipy.linalg import inv
import matplotlib.pyplot as plt
import seaborn as sns
import re
from io import BytesIO
import base64
import networkx as nx

# ==================== KONFIGURASI ====================
st.set_page_config(
    page_title="Sistem Rekording Ternak - Unsoed",
    page_icon="🐄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== INISIALISASI SESSION STATE ====================
if 'pedigree' not in st.session_state:
    st.session_state.pedigree = None
if 'results' not in st.session_state:
    st.session_state.results = {}
if 'generations' not in st.session_state:
    st.session_state.generations = None
if 'input_method' not in st.session_state:
    st.session_state.input_method = "Upload File"

# ==================== FUNGSI UNTUK BACKGROUND ====================
def add_background():
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .main > div {
        background: rgba(255, 255, 255, 0.92);
        border-radius: 15px;
        padding: 20px;
        margin: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .css-1d391kg {
        background: rgba(44, 62, 80, 0.95) !important;
        backdrop-filter: blur(10px);
    }
    .css-1d391kg .stMarkdown, .css-1d391kg .stText, .css-1d391kg .stTitle {
        color: white !important;
    }
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3 {
        color: #f1c40f !important;
    }
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: rgba(44, 62, 80, 0.95);
        backdrop-filter: blur(10px);
        color: white;
        text-align: center;
        padding: 10px 20px;
        font-size: 14px;
        border-top: 3px solid #f1c40f;
        z-index: 999;
    }
    .footer-content {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 30px;
        flex-wrap: wrap;
    }
    .footer-item {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .footer-item .label {
        font-weight: bold;
        color: #f1c40f;
    }
    .footer-item .value {
        color: #ecf0f1;
    }
    .main-header {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin-bottom: 20px;
        text-align: center;
    }
    .main-header h1 {
        color: #f1c40f !important;
        margin: 0;
    }
    .main-header p {
        color: #ecf0f1;
        margin: 5px 0 0 0;
    }
    .st-emotion-cache-1cypcdb {
        display: none !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,0.5);
        border-radius: 10px;
        padding: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 20px;
        background: rgba(255,255,255,0.7);
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(241, 196, 15, 0.3);
    }
    .stTabs [aria-selected="true"] {
        background: #f1c40f !important;
        color: #2c3e50 !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

def add_footer():
    footer_html = """
    <div class="footer" style="background: rgba(44, 62, 80, 0.95); backdrop-filter: blur(10px); color: white; text-align: center; padding: 10px 20px; font-size: 14px; border-top: 3px solid #f1c40f; z-index: 999; position: fixed; bottom: 0; left: 0; right: 0;">
        <div style="display: flex; flex-wrap: wrap; justify-content: center; align-items: center; gap: 8px 25px; max-width: 1200px; margin: 0 auto;">
            
            <!-- Developed by -->
            <div style="display: flex; align-items: center; gap: 5px;">
                <span style="font-weight: bold; color: #f1c40f;">🐄 Developed by:</span>
                <span style="color: #ecf0f1;">Agus Susanto</span>
            </div>
            
            <!-- Lab -->
            <div style="display: flex; align-items: center; gap: 5px;">
                <span style="font-weight: bold; color: #f1c40f;">🏛️ Lab:</span>
                <span style="color: #ecf0f1;">Pemuliaan Ternak Terapan</span>
            </div>
            
            <!-- Kerjasama -->
            <div style="display: flex; align-items: center; gap: 5px; flex-wrap: wrap; justify-content: center;">
                <span style="font-weight: bold; color: #f1c40f;">🤝 Kerjasama:</span>
                <span style="color: #ecf0f1; font-size: 12px;">
                    Fakultas Peternakan Universitas Jenderal Soedirman
                    <span style="color: #f1c40f; margin: 0 5px;">|</span>
                    dengan
                    <span style="color: #f1c40f; margin: 0 5px;">|</span>
                    Balai Besar Pembibitan Ternak Unggul dan Hijauan Pakan Ternak (BBPTUHPT) Baturraden
                </span>
            </div>
            
        </div>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

def add_sidebar_identity():
    sidebar_html = """
    <style>
    .sidebar-identity {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 15px;
        margin-top: 20px;
        border: 1px solid rgba(241, 196, 15, 0.3);
    }
    .sidebar-identity .title {
        color: #f1c40f;
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 5px;
    }
    .sidebar-identity .subtitle {
        color: #ecf0f1;
        font-size: 13px;
        margin: 2px 0;
    }
    .sidebar-identity .divider {
        border: none;
        border-top: 1px solid rgba(241, 196, 15, 0.2);
        margin: 10px 0;
    }
    </style>
    <div class="sidebar-identity">
        <div class="title">🐄 Sistem Rekording Ternak</div>
        <hr class="divider">
        <div class="subtitle">👨‍💻 Developed by: <b>Agus Susanto</b></div>
        <div class="subtitle">🏛️ Animal Breeding Lab</div>
        <div class="subtitle">📚 Fakultas Peternakan</div>
        <div class="subtitle">🎓 Universitas Jenderal Soedirman</div>
        <hr class="divider">
        <div class="subtitle" style="font-size: 11px; color: #bdc3c7;">
            © 2026 - All Rights Reserved
        </div>
    </div>
    """
    st.sidebar.markdown(sidebar_html, unsafe_allow_html=True)

# ==================== FUNGSI VALIDASI SEX ====================
def validate_sex(df):
    df_copy = df.copy()
    errors = []
    warnings = []
    
    sex_col = None
    for col in df_copy.columns:
        if col.lower() in ['sex', 'jenis_kelamin', 'gender', 'kelamin']:
            sex_col = col
            break
    
    for col in ['ID', 'Sire', 'Dam']:
        if col in df_copy.columns:
            df_copy[col] = df_copy[col].astype(str).str.strip()
            df_copy[col] = df_copy[col].replace('nan', '0')
            df_copy[col] = df_copy[col].replace('None', '0')
    
    sex_map = {}
    if sex_col:
        for _, row in df_copy.iterrows():
            id_val = row['ID']
            sex_val = str(row[sex_col]).upper().strip()
            if sex_val in ['M', 'MALE', 'JANTAN', 'J', 'L', 'LAKI', '1']:
                sex_map[id_val] = 'MALE'
            elif sex_val in ['F', 'FEMALE', 'BETINA', 'P', 'PEREMPUAN', '2']:
                sex_map[id_val] = 'FEMALE'
            elif sex_val in ['0', '']:
                sex_map[id_val] = 'UNKNOWN'
            else:
                sex_map[id_val] = sex_val
    
    duplicate_sex = {}
    for _, row in df_copy.iterrows():
        id_val = row['ID']
        if sex_col:
            sex_val = str(row[sex_col]).upper().strip()
            if id_val in duplicate_sex:
                if duplicate_sex[id_val] != sex_val:
                    errors.append(f"❌ Individu '{id_val}' memiliki jenis kelamin ganda: '{duplicate_sex[id_val]}' dan '{sex_val}'")
            else:
                duplicate_sex[id_val] = sex_val
    
    for _, row in df_copy.iterrows():
        sire = row['Sire']
        if sire != '0' and sire in sex_map:
            sire_sex = sex_map[sire]
            if sire_sex == 'FEMALE':
                errors.append(f"❌ Individu '{sire}' adalah BETINA tetapi digunakan sebagai SIRE (jantan)!")
            elif sire_sex == 'UNKNOWN':
                warnings.append(f"⚠️ Jenis kelamin Sire '{sire}' tidak diketahui. Asumsikan sebagai jantan.")
    
    for _, row in df_copy.iterrows():
        dam = row['Dam']
        if dam != '0' and dam in sex_map:
            dam_sex = sex_map[dam]
            if dam_sex == 'MALE':
                errors.append(f"❌ Individu '{dam}' adalah JANTAN tetapi digunakan sebagai DAM (betina)!")
            elif dam_sex == 'UNKNOWN':
                warnings.append(f"⚠️ Jenis kelamin Dam '{dam}' tidak diketahui. Asumsikan sebagai betina.")
    
    sire_set = set()
    dam_set = set()
    for _, row in df_copy.iterrows():
        if row['Sire'] != '0':
            sire_set.add(row['Sire'])
        if row['Dam'] != '0':
            dam_set.add(row['Dam'])
    
    conflict_ids = sire_set.intersection(dam_set)
    for id_val in conflict_ids:
        errors.append(f"❌ Individu '{id_val}' muncul sebagai SIRE dan DAM sekaligus! (harus salah satu)")
    
    if sex_col:
        sex_groups = {}
        for _, row in df_copy.iterrows():
            id_val = row['ID']
            sex_val = str(row[sex_col]).upper().strip()
            if id_val not in sex_groups:
                sex_groups[id_val] = set()
            sex_groups[id_val].add(sex_val)
        
        for id_val, sexes in sex_groups.items():
            if len(sexes) > 1:
                errors.append(f"❌ Individu '{id_val}' memiliki data sex ganda: {', '.join(sexes)}")
    
    if sex_col is None:
        warnings.append("ℹ️ Tidak ada kolom SEX. Sistem akan mengasumsikan sex berdasarkan peran (Sire/Dam).")
        sex_temp = {}
        for _, row in df_copy.iterrows():
            id_val = row['ID']
            if id_val in sire_set and id_val not in dam_set:
                sex_temp[id_val] = 'MALE'
            elif id_val in dam_set and id_val not in sire_set:
                sex_temp[id_val] = 'FEMALE'
            elif id_val not in sire_set and id_val not in dam_set:
                sex_temp[id_val] = 'UNKNOWN'
            else:
                sex_temp[id_val] = 'UNKNOWN'
        
        df_copy['SEX'] = df_copy['ID'].map(sex_temp)
    
    return df_copy, errors, warnings

# ==================== FUNGSI BANTU ====================
def natural_sort_key(id_string):
    def convert(text):
        return int(text) if text.isdigit() else text.lower()
    parts = re.split('([0-9]+)', str(id_string))
    return [convert(part) for part in parts]

def sort_pedigree(df):
    df_copy = df.copy()
    
    for col in ['ID', 'Sire', 'Dam']:
        df_copy[col] = df_copy[col].astype(str).str.strip()
        df_copy[col] = df_copy[col].replace('nan', '0')
        df_copy[col] = df_copy[col].replace('None', '0')
    
    id_list = df_copy['ID'].tolist()
    id_set = set(id_list)
    
    def get_generation(indiv_id, visited=None):
        if visited is None:
            visited = set()
        if indiv_id in visited:
            return 0
        visited.add(indiv_id)
        
        row = df_copy[df_copy['ID'] == indiv_id]
        if row.empty:
            return 0
        
        sire = row.iloc[0]['Sire']
        dam = row.iloc[0]['Dam']
        
        gen_sire = 0
        gen_dam = 0
        
        if sire != '0' and sire in id_set:
            gen_sire = get_generation(sire, visited.copy())
        if dam != '0' and dam in id_set:
            gen_dam = get_generation(dam, visited.copy())
        
        return 1 + max(gen_sire, gen_dam)
    
    generations = {}
    for indiv in id_list:
        try:
            generations[indiv] = get_generation(indiv)
        except RecursionError:
            generations[indiv] = 0
    
    df_copy['_generation'] = df_copy['ID'].map(generations)
    df_copy['_sort_key'] = df_copy.apply(
        lambda row: (row['_generation'], natural_sort_key(row['ID'])), 
        axis=1
    )
    
    df_sorted = df_copy.sort_values('_sort_key').drop(['_generation', '_sort_key'], axis=1)
    df_sorted = df_sorted.reset_index(drop=True)
    
    return df_sorted, generations

def detect_cycle(df):
    df_copy = df.copy()
    id_set = set(df_copy['ID'].tolist())
    
    graph = {id_: [] for id_ in id_set}
    for _, row in df_copy.iterrows():
        child = row['ID']
        sire = row['Sire']
        dam = row['Dam']
        if sire != '0' and sire in id_set:
            graph[sire].append(child)
        if dam != '0' and dam in id_set:
            graph[dam].append(child)
    
    visited = set()
    recursion_stack = set()
    
    def has_cycle(node):
        visited.add(node)
        recursion_stack.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if has_cycle(neighbor):
                    return True
            elif neighbor in recursion_stack:
                return True
        recursion_stack.remove(node)
        return False
    
    for node in graph:
        if node not in visited:
            if has_cycle(node):
                return True
    return False

def standardize_columns(df):
    df_copy = df.copy()
    
    column_mapping = {}
    for col in df_copy.columns:
        col_lower = col.lower().strip()
        if col_lower in ['id', 'calf', 'animal', 'individu', 'individual', 'no', 'nomor']:
            column_mapping[col] = 'ID'
        elif col_lower in ['sire', 'father', 'ayah', 'jantan', 'pejantan', 'bapak']:
            column_mapping[col] = 'Sire'
        elif col_lower in ['dam', 'mother', 'ibu', 'betina', 'induk', 'dams']:
            column_mapping[col] = 'Dam'
        elif col_lower in ['sex', 'jenis_kelamin', 'gender', 'kelamin']:
            column_mapping[col] = 'SEX'
    
    if 'ID' not in column_mapping.values() and len(df_copy.columns) > 0:
        first_col = df_copy.columns[0]
        column_mapping[first_col] = 'ID'
    
    df_copy = df_copy.rename(columns=column_mapping)
    
    required_cols = ['ID', 'Sire', 'Dam']
    for col in required_cols:
        if col not in df_copy.columns:
            df_copy[col] = '0'
    
    for col in ['ID', 'Sire', 'Dam']:
        df_copy[col] = df_copy[col].astype(str).str.strip()
        df_copy[col] = df_copy[col].replace('nan', '0')
        df_copy[col] = df_copy[col].replace('None', '0')
    
    return df_copy

def complete_pedigree(df):
    df_copy = df.copy()
    existing_ids = set(df_copy['ID'].tolist())
    
    missing_ids = set()
    for sire in df_copy['Sire']:
        if sire != '0' and sire not in existing_ids:
            missing_ids.add(sire)
    for dam in df_copy['Dam']:
        if dam != '0' and dam not in existing_ids:
            missing_ids.add(dam)
    
    if missing_ids:
        for missing_id in sorted(missing_ids, key=natural_sort_key):
            new_row = pd.DataFrame({
                'ID': [missing_id],
                'Sire': ['0'],
                'Dam': ['0'],
                'SEX': ['UNKNOWN']
            })
            df_copy = pd.concat([df_copy, new_row], ignore_index=True)
    
    return df_copy

def process_pedigree_data(df_raw):
    df_standard = standardize_columns(df_raw)
    df_validated, errors, warnings = validate_sex(df_standard)
    
    if errors:
        error_msg = "\n".join(errors)
        return None, None, error_msg, warnings
    
    df_completed = complete_pedigree(df_validated)
    
    has_cycle = detect_cycle(df_completed)
    if has_cycle:
        return None, None, "⚠️ Terdeteksi siklus dalam pedigree!", warnings
    
    df_sorted, generations = sort_pedigree(df_completed)
    
    return df_sorted, generations, None, warnings

# ==================== FUNGSI PERHITUNGAN ====================
def hitung_inbreeding_dan_matriks_A(silsilah_df):
    df = silsilah_df[['ID', 'Sire', 'Dam']].copy()
    
    for col in ['ID', 'Sire', 'Dam']:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace('nan', '0')
        df[col] = df[col].replace('None', '0')
    
    id_list = df['ID'].tolist()
    n = len(id_list)
    id_to_idx = {id_: i for i, id_ in enumerate(id_list)}
    
    A = np.zeros((n, n))
    F = np.zeros(n)
    
    for i in range(n):
        sire = df.loc[i, 'Sire']
        dam = df.loc[i, 'Dam']
        
        sire_idx = id_to_idx.get(sire) if sire != '0' else None
        dam_idx = id_to_idx.get(dam) if dam != '0' else None
        
        if sire_idx is None and dam_idx is None:
            A[i, i] = 1.0
            F[i] = 0.0
            
        elif sire_idx is not None and dam_idx is None:
            A[i, i] = 1.0
            F[i] = 0.0
            A[i, sire_idx] = 0.5 * A[sire_idx, sire_idx]
            A[sire_idx, i] = A[i, sire_idx]
            for j in range(n):
                if j != i and j != sire_idx:
                    A[i, j] = 0.5 * A[sire_idx, j]
                    A[j, i] = A[i, j]
                    
        elif sire_idx is None and dam_idx is not None:
            A[i, i] = 1.0
            F[i] = 0.0
            A[i, dam_idx] = 0.5 * A[dam_idx, dam_idx]
            A[dam_idx, i] = A[i, dam_idx]
            for j in range(n):
                if j != i and j != dam_idx:
                    A[i, j] = 0.5 * A[dam_idx, j]
                    A[j, i] = A[i, j]
        
        else:
            a_sire_dam = A[sire_idx, dam_idx]
            F[i] = 0.5 * a_sire_dam
            A[i, i] = 1.0 + F[i]
            
            A[i, sire_idx] = 0.5 * (A[sire_idx, sire_idx] + A[sire_idx, dam_idx])
            A[sire_idx, i] = A[i, sire_idx]
            
            A[i, dam_idx] = 0.5 * (A[dam_idx, sire_idx] + A[dam_idx, dam_idx])
            A[dam_idx, i] = A[i, dam_idx]
            
            for j in range(n):
                if j != i and j != sire_idx and j != dam_idx:
                    A[i, j] = 0.5 * (A[sire_idx, j] + A[dam_idx, j])
                    A[j, i] = A[i, j]
    
    A_df = pd.DataFrame(A, index=id_list, columns=id_list)
    F_dict = dict(zip(id_list, F))
    
    return F_dict, A_df, A, id_list

# ==================== FUNGSI PEDIGREE CHART (DENGAN WARNA EDGE) ====================
def create_pedigree_chart(df, F_dict=None):
    G = nx.DiGraph()
    
    for _, row in df.iterrows():
        id_val = row['ID']
        sex = 'U'
        if 'SEX' in row:
            sex_val = str(row['SEX']).upper().strip()
            if sex_val in ['M', 'MALE', 'JANTAN', 'J', 'L', 'LAKI', '1']:
                sex = 'M'
            elif sex_val in ['F', 'FEMALE', 'BETINA', 'P', 'PEREMPUAN', '2']:
                sex = 'F'
        
        G.add_node(id_val, sex=sex)
    
    for _, row in df.iterrows():
        child = row['ID']
        sire = row['Sire']
        dam = row['Dam']
        
        if sire != '0' and sire in G.nodes:
            G.add_edge(sire, child, type='sire')
        if dam != '0' and dam in G.nodes:
            G.add_edge(dam, child, type='dam')
    
    generations = {}
    if hasattr(st.session_state, 'generations') and st.session_state.generations:
        generations = st.session_state.generations
    else:
        for node in nx.topological_sort(G):
            if G.in_degree(node) == 0:
                generations[node] = 0
            else:
                max_gen = 0
                for pred in G.predecessors(node):
                    if pred in generations:
                        max_gen = max(max_gen, generations[pred] + 1)
                generations[node] = max_gen
    
    return G, generations

def draw_pedigree_chart(G, generations, F_dict=None, title="Pedigree Chart", show_f=True):
    """
    Menggambar pedigree chart dengan garis hubungan yang tipis dan rapi
    """
    pos = {}
    
    gen_groups = {}
    for node, gen in generations.items():
        if gen not in gen_groups:
            gen_groups[gen] = []
        gen_groups[gen].append(node)
    
    max_gen = max(generations.values()) if generations else 0
    
    for gen in range(max_gen + 1):
        nodes_in_gen = gen_groups.get(gen, [])
        n_nodes = len(nodes_in_gen)
        for i, node in enumerate(sorted(nodes_in_gen)):
            x = (i + 0.5) / n_nodes if n_nodes > 0 else 0.5
            y = 1 - (gen / (max_gen + 2)) if max_gen > 0 else 0.5
            pos[node] = (x * 10, y * 10)
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # ============================================================
    # WARNA NODE BERDASARKAN JENIS KELAMIN
    # ============================================================
    node_colors = []
    for node in G.nodes():
        sex = G.nodes[node].get('sex', 'U')
        if sex == 'M':
            node_colors.append('#3498db')
        elif sex == 'F':
            node_colors.append('#e74c3c')
        else:
            node_colors.append('#95a5a6')
    
    node_sizes = []
    for node in G.nodes():
        if F_dict and node in F_dict:
            f_val = F_dict[node]
            size = 800 + (f_val * 2000)
            node_sizes.append(size)
        else:
            node_sizes.append(800)
    
    nx.draw_networkx_nodes(G, pos, 
                          node_color=node_colors, 
                          node_size=node_sizes,
                          alpha=0.9,
                          edgecolors='black',
                          linewidths=2,
                          ax=ax)
    
    # ============================================================
    # EDGE DENGAN LINE WIDTH YANG LEBIH TIPIS
    # ============================================================
    edges_sire = []
    edges_dam = []
    edges_unknown = []
    
    for u, v, data in G.edges(data=True):
        sex = G.nodes[u].get('sex', 'U')
        if sex == 'M':
            edges_sire.append((u, v))
        elif sex == 'F':
            edges_dam.append((u, v))
        else:
            edges_unknown.append((u, v))
    
    # ============================================================
    # LINE WIDTH DIPERKECIL: 2.5 → 1.2
    # ============================================================
    if edges_sire:
        nx.draw_networkx_edges(G, pos,
                              edgelist=edges_sire,
                              edge_color='#3498db',
                              arrows=True,
                              arrowsize=15,
                              arrowstyle='->',
                              width=1.2,       # <-- Lebih tipis
                              alpha=0.7,
                              ax=ax)
    
    if edges_dam:
        nx.draw_networkx_edges(G, pos,
                              edgelist=edges_dam,
                              edge_color='#e74c3c',
                              arrows=True,
                              arrowsize=15,
                              arrowstyle='->',
                              width=1.2,       # <-- Lebih tipis
                              alpha=0.7,
                              ax=ax)
    
    if edges_unknown:
        nx.draw_networkx_edges(G, pos,
                              edgelist=edges_unknown,
                              edge_color='#95a5a6',
                              arrows=True,
                              arrowsize=15,
                              arrowstyle='->',
                              width=1.0,       # <-- Lebih tipis
                              alpha=0.5,
                              ax=ax)
    
    # ============================================================
    # LABEL NODE
    # ============================================================
    labels = {}
    for node in G.nodes():
        if F_dict and node in F_dict and show_f:
            labels[node] = f"{node}\nF={F_dict[node]:.3f}"
        else:
            labels[node] = f"{node}"
    
    nx.draw_networkx_labels(G, pos, labels, font_size=9, font_weight='bold', ax=ax)
    
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.axis('off')
    
    # ============================================================
    # LEGENDA (dengan line width yang disesuaikan)
    # ============================================================
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#3498db', 
                   markersize=12, label='Jantan (M)'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#e74c3c', 
                   markersize=12, label='Betina (F)'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#95a5a6', 
                   markersize=12, label='Unknown'),
        plt.Line2D([0], [0], color='#3498db', lw=1.5, label='Hubungan dari Sire (Jantan)'),
        plt.Line2D([0], [0], color='#e74c3c', lw=1.5, label='Hubungan dari Dam (Betina)'),
        plt.Line2D([0], [0], color='#95a5a6', lw=1.0, label='Hubungan dari Unknown'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
    
    plt.tight_layout()
    return fig

# ==================== FUNGSI CROSSCHECKING PERKAWINAN ====================
def cek_perkawinan(sire_id, dam_id, A_df, id_list):
    if sire_id not in id_list:
        return {"error": f"ID Sire '{sire_id}' tidak ditemukan dalam data!"}
    if dam_id not in id_list:
        return {"error": f"ID Dam '{dam_id}' tidak ditemukan dalam data!"}
    
    a_sire_dam = A_df.loc[sire_id, dam_id]
    F_anak = 0.5 * a_sire_dam
    F_sire = A_df.loc[sire_id, sire_id] - 1
    F_dam = A_df.loc[dam_id, dam_id] - 1
    
    if F_anak == 0:
        status = "✅ AMAN - Tidak ada inbreeding"
        color = "green"
        detail = "Tidak ada hubungan kekerabatan antara kedua individu."
    elif F_anak < 0.0625:
        status = "🟢 RENDAH - Inbreeding sangat rendah"
        color = "lightgreen"
        detail = "Masih aman untuk pemuliaan, risiko rendah."
    elif F_anak < 0.125:
        status = "🟡 SEDANG - Terdapat inbreeding"
        color = "orange"
        detail = "Perlu dipertimbangkan, mungkin masih bisa diterima."
    elif F_anak < 0.25:
        status = "🟠 TINGGI - Inbreeding signifikan"
        color = "red"
        detail = "Sangat disarankan untuk menghindari perkawinan ini!"
    else:
        status = "🔴 SANGAT TINGGI - Inbreeding ekstrem"
        color = "darkred"
        detail = "HARUS DIHINDARI! Dapat menyebabkan inbreeding depression!"
    
    hubungan = []
    if sire_id == dam_id:
        hubungan.append("⚠️ SELFING - Individu yang sama!")
    else:
        pedigree_data = st.session_state.pedigree
        if pedigree_data is not None:
            for _, row in pedigree_data.iterrows():
                if row['ID'] == dam_id:
                    if row['Sire'] == sire_id:
                        hubungan.append("👨‍👧 Sire adalah AYAH dari Dam")
                    if row['Dam'] == sire_id:
                        hubungan.append("👩‍👧 Sire adalah IBU dari Dam")
                if row['ID'] == sire_id:
                    if row['Sire'] == dam_id:
                        hubungan.append("👨‍👧 Dam adalah AYAH dari Sire")
                    if row['Dam'] == dam_id:
                        hubungan.append("👩‍👧 Dam adalah IBU dari Sire")
    
    return {
        "sire_id": sire_id,
        "dam_id": dam_id,
        "a_sire_dam": a_sire_dam,
        "F_anak": F_anak,
        "F_sire": F_sire,
        "F_dam": F_dam,
        "status": status,
        "color": color,
        "detail": detail,
        "hubungan": hubungan
    }

# ==================== TAMPILAN UTAMA ====================
add_background()
add_footer()

# ==================== SIDEBAR ====================
with st.sidebar:
    st.title("🐄 Menu")
    
    menu = st.radio(
        "Navigasi",
        ["🏠 Dashboard", "📊 Data Entry", "🔬 Analisis", "🧬 Pedigree Chart", "🤝 Cek Perkawinan", "📈 Laporan"]
    )
    
    st.divider()
    
    if st.session_state.pedigree is not None:
        st.success(f"✅ Data tersedia: {len(st.session_state.pedigree)} individu")
    else:
        st.info("📌 Belum ada data")
    
    add_sidebar_identity()

# ================================================================
# MENU: DASHBOARD
# ================================================================
if menu == "🏠 Dashboard":
    st.markdown("""
    <div class="main-header">
        <h1>🐄 Sistem Rekording dan Analisis Genetik Ternak</h1>
        <p>Manajemen Data Pedigree, Perhitungan Inbreeding, dan Matriks Kekerabatan</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### Selamat datang di Sistem Manajemen Rekording Ternak
    
    **Fitur:**
    - ✅ Mencatat data silsilah dan fenotipik ternak
    - ✅ **Validasi Jenis Kelamin Otomatis**
    - ✅ 4 Metode Input Data
    - ✅ Auto-sorting berdasarkan generasi + ID
    - ✅ Menghitung koefisien inbreeding (F) dengan algoritma Henderson
    - ✅ Membangun matriks kekerabatan (A) yang akurat
    - ✅ **🧬 Pedigree Chart - Visualisasi silsilah dengan warna edge berdasarkan jenis kelamin tetua**
    - ✅ Cek perkawinan - Prediksi inbreeding anak
    """)
    
    if st.session_state.pedigree is not None:
        df = st.session_state.pedigree
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Individu", len(df))
        with col2:
            known_sire = sum(df['Sire'] != '0')
            st.metric("Sire Diketahui", f"{known_sire} ({known_sire/len(df)*100:.1f}%)")
        with col3:
            known_dam = sum(df['Dam'] != '0')
            st.metric("Dam Diketahui", f"{known_dam} ({known_dam/len(df)*100:.1f}%)")
        with col4:
            if 'SEX' in df.columns:
                male_count = sum(df['SEX'].astype(str).str.upper().str.strip().isin(['MALE', 'M', 'JANTAN', 'J', 'L', 'LAKI']))
                female_count = sum(df['SEX'].astype(str).str.upper().str.strip().isin(['FEMALE', 'F', 'BETINA', 'P', 'PEREMPUAN']))
                st.metric("Sex", f"👨{male_count} / 👩{female_count}")

# ================================================================
# MENU: DATA ENTRY
# ================================================================
elif menu == "📊 Data Entry":
    st.markdown("""
    <div class="main-header">
        <h1>📊 Data Entry - Input Data Pedigree</h1>
        <p>Upload file, input manual, bulk input, atau edit data langsung</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📤 Upload File",
        "✏️ Input Manual",
        "📋 Bulk Input",
        "📊 Data Editor"
    ])
    
    with tab1:
        st.subheader("Upload File CSV atau Excel")
        st.caption("Format: ID, Sire, Dam, SEX (opsional)")
        
        uploaded = st.file_uploader(
            "Pilih file CSV atau Excel",
            type=['csv', 'xlsx'],
            key="upload_tab"
        )
        
        if uploaded is not None:
            try:
                if uploaded.name.endswith('.csv'):
                    df_raw = pd.read_csv(uploaded)
                else:
                    df_raw = pd.read_excel(uploaded)
                
                st.write("📋 **Preview data yang diupload:**")
                st.dataframe(df_raw.head())
                
                if st.button("✅ Proses Data dari File", key="process_upload"):
                    df_sorted, generations, error, warnings = process_pedigree_data(df_raw)
                    
                    if error:
                        st.error(error)
                    if warnings:
                        for w in warnings:
                            st.warning(w)
                    if not error:
                        st.session_state.pedigree = df_sorted
                        st.session_state.generations = generations
                        st.success(f"✅ {len(df_sorted)} data berhasil diproses!")
                        st.rerun()
                        
            except Exception as e:
                st.error(f"Error membaca file: {str(e)}")
        
        st.divider()
        st.subheader("📥 Download Template")
        
        template_df = pd.DataFrame({
            'ID': ['Sapi-01', 'Sapi-02', 'Sapi-03'],
            'SIRE': ['0', '0', 'Sapi-01'],
            'DAM': ['0', '0', 'Sapi-02'],
            'SEX': ['M', 'F', 'F']
        })
        
        csv_template = template_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Template CSV",
            data=csv_template,
            file_name='template_pedigree.csv',
            mime='text/csv'
        )
    
    with tab2:
        st.subheader("Input Data Pedigree Satu Per Satu")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            id_baru = st.text_input("🆔 ID Individu", placeholder="Contoh: A001")
        
        with col2:
            sire_baru = st.text_input("👨 Sire (Ayah)", placeholder="ID Ayah atau 0")
        
        with col3:
            dam_baru = st.text_input("👩 Dam (Ibu)", placeholder="ID Ibu atau 0")
        
        with st.expander("📊 Data Tambahan (Opsional)"):
            col1, col2 = st.columns(2)
            with col1:
                sex_baru = st.selectbox("Jenis Kelamin", ["", "M (Jantan)", "F (Betina)"])
            with col2:
                fenotip_baru = st.text_input("Data Fenotipik", placeholder="Contoh: 450 kg")
        
        if st.button("➕ Tambahkan Individu", type="primary"):
            if not id_baru:
                st.warning("⚠️ ID Individu harus diisi!")
            else:
                new_row = pd.DataFrame({
                    'ID': [id_baru],
                    'Sire': [sire_baru if sire_baru else '0'],
                    'Dam': [dam_baru if dam_baru else '0']
                })
                
                if sex_baru:
                    sex_value = 'M' if 'Jantan' in sex_baru else 'F'
                    new_row['SEX'] = sex_value
                if fenotip_baru:
                    new_row['Data_Fenotipik'] = fenotip_baru
                
                if st.session_state.pedigree is not None:
                    df_combined = pd.concat([st.session_state.pedigree, new_row], ignore_index=True)
                else:
                    df_combined = new_row
                
                df_sorted, generations, error, warnings = process_pedigree_data(df_combined)
                
                if error:
                    st.error(error)
                if warnings:
                    for w in warnings:
                        st.warning(w)
                if not error:
                    st.session_state.pedigree = df_sorted
                    st.session_state.generations = generations
                    st.success(f"✅ Individu '{id_baru}' berhasil ditambahkan!")
                    st.rerun()
        
        if st.session_state.pedigree is not None and not st.session_state.pedigree.empty:
            st.divider()
            st.subheader("📋 Data Saat Ini")
            st.dataframe(st.session_state.pedigree, use_container_width=True, hide_index=True)
    
    with tab3:
        st.subheader("Bulk Input - Paste Data dalam Format Tabel")
        
        with st.expander("📖 Lihat Format Contoh"):
            st.code("""
ID,SIRE,DAM,SEX
1,0,0,M
2,0,0,F
3,0,0,M
4,1,0,M
5,3,2,F
6,1,2,F
7,4,5,M
8,3,6,M
            """, language="text")
            st.caption("📌 SEX: M untuk Jantan, F untuk Betina")
        
        bulk_data = st.text_area(
            "📝 Paste data di sini",
            placeholder="ID,SIRE,DAM,SEX\n1,0,0,M\n2,0,0,F\n3,0,0,M\n4,1,0,M\n5,3,2,F\n6,1,2,F\n7,4,5,M\n8,3,6,M",
            height=200
        )
        
        if st.button("✅ Proses Bulk Data", type="primary"):
            if not bulk_data.strip():
                st.warning("⚠️ Silakan paste data terlebih dahulu!")
            else:
                try:
                    lines = bulk_data.strip().split('\n')
                    header = [h.strip() for h in lines[0].split(',')]
                    
                    data_rows = []
                    for line in lines[1:]:
                        if line.strip():
                            values = [v.strip() for v in line.split(',')]
                            if len(values) == len(header):
                                data_rows.append(values)
                    
                    if not data_rows:
                        st.warning("⚠️ Tidak ada data yang valid!")
                    else:
                        df_bulk = pd.DataFrame(data_rows, columns=header)
                        st.write("📋 **Preview data yang akan diproses:**")
                        st.dataframe(df_bulk)
                        
                        df_sorted, generations, error, warnings = process_pedigree_data(df_bulk)
                        
                        if error:
                            st.error(error)
                        if warnings:
                            for w in warnings:
                                st.warning(w)
                        if not error:
                            st.session_state.pedigree = df_sorted
                            st.session_state.generations = generations
                            st.success(f"✅ {len(df_sorted)} data berhasil diproses!")
                            st.rerun()
                            
                except Exception as e:
                    st.error(f"Error memproses data: {str(e)}")
        
        if st.session_state.pedigree is not None and not st.session_state.pedigree.empty:
            st.divider()
            st.subheader("📋 Data Saat Ini")
            st.dataframe(st.session_state.pedigree, use_container_width=True, hide_index=True)
    
    with tab4:
        st.subheader("📊 Edit Data Langsung di Tabel")
        
        if st.session_state.pedigree is not None and not st.session_state.pedigree.empty:
            edited_df = st.data_editor(
                st.session_state.pedigree,
                num_rows="dynamic",
                use_container_width=True,
                key="data_editor"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Simpan Perubahan", type="primary"):
                    df_sorted, generations, error, warnings = process_pedigree_data(edited_df)
                    
                    if error:
                        st.error(error)
                    if warnings:
                        for w in warnings:
                            st.warning(w)
                    if not error:
                        st.session_state.pedigree = df_sorted
                        st.session_state.generations = generations
                        st.success(f"✅ {len(df_sorted)} data berhasil diperbarui!")
                        st.rerun()
            
            with col2:
                if st.button("🗑️ Hapus Semua Data", type="secondary"):
                    st.session_state.pedigree = None
                    st.session_state.generations = None
                    st.session_state.results = {}
                    st.success("🗑️ Semua data berhasil dihapus!")
                    st.rerun()
        else:
            st.info("📌 Belum ada data.")

# ================================================================
# MENU: ANALISIS
# ================================================================
elif menu == "🔬 Analisis":
    st.markdown("""
    <div class="main-header">
        <h1>🔬 Analisis Genetik</h1>
        <p>Hitung Koefisien Inbreeding dan Matriks Kekerabatan</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.pedigree is not None:
        with st.expander("📋 Data yang akan dianalisis", expanded=True):
            st.dataframe(st.session_state.pedigree)
            
            if st.session_state.generations is not None:
                gen_data = []
                for id_, gen in st.session_state.generations.items():
                    gen_data.append({'ID': id_, 'Generasi': gen})
                gen_df = pd.DataFrame(gen_data).sort_values(['Generasi', 'ID'])
                st.caption("📊 Generasi setiap individu:")
                st.dataframe(gen_df, hide_index=True)
        
        if st.button("🚀 Hitung Koefisien Inbreeding & Matriks A", type="primary"):
            with st.spinner("🔄 Sedang memproses data..."):
                try:
                    F_dict, A_df, A, id_list = hitung_inbreeding_dan_matriks_A(st.session_state.pedigree)
                    
                    st.session_state.results['F'] = F_dict
                    st.session_state.results['A'] = A_df
                    st.session_state.results['id_list'] = id_list
                    st.success("✅ Analisis selesai!")
                except Exception as e:
                    st.error(f"Error dalam perhitungan: {str(e)}")
        
        if 'F' in st.session_state.results:
            # ============================================================
            # KOEFISIEN INBREEDING (F) - DENGAN URUTAN ID
            # ============================================================
            with st.expander("📈 Koefisien Inbreeding (F)", expanded=True):
                # Buat DataFrame dari hasil F
                F_df = pd.DataFrame(
                    st.session_state.results['F'].items(),
                    columns=['ID', 'Koefisien Inbreeding']
                )
                
                # Urutkan ID menggunakan natural_sort_key
                F_df['_sort_key'] = F_df['ID'].apply(natural_sort_key)
                F_df = F_df.sort_values('_sort_key').drop('_sort_key', axis=1)
                F_df = F_df.reset_index(drop=True)
                
                # Statistik
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Rata-rata F", f"{F_df['Koefisien Inbreeding'].mean():.4f}")
                with col2:
                    st.metric("⬆️ Maksimum F", f"{F_df['Koefisien Inbreeding'].max():.4f}")
                with col3:
                    st.metric("⬇️ Minimum F", f"{F_df['Koefisien Inbreeding'].min():.4f}")
                
                # Tabel dengan warna gradasi
                st.dataframe(
                    F_df.style.background_gradient(
                        cmap='RdYlGn_r',
                        subset=['Koefisien Inbreeding']
                    ),
                    use_container_width=True,
                    hide_index=True
                )
            
            # ============================================================
            # MATRIKS KEKERABATAN (A)
            # ============================================================
            with st.expander("📊 Matriks Kekerabatan (A)", expanded=True):
                if st.session_state.results['A'] is not None:
                    A_df = st.session_state.results['A']
                    
                    # Urutkan kolom dan index berdasarkan ID
                    sorted_ids = sorted(A_df.index.tolist(), key=natural_sort_key)
                    A_df = A_df.loc[sorted_ids, sorted_ids]
                    
                    st.dataframe(
                        A_df.style.background_gradient(
                            cmap='Blues', 
                            axis=None, 
                            vmin=0, 
                            vmax=2
                        ),
                        use_container_width=True
                    )
            
            # ============================================================
            # HEATMAP
            # ============================================================
            with st.expander("🔥 Heatmap", expanded=True):
                if st.session_state.results['A'] is not None:
                    try:
                        A_df = st.session_state.results['A']
                        
                        # Urutkan kolom dan index berdasarkan ID
                        sorted_ids = sorted(A_df.index.tolist(), key=natural_sort_key)
                        A_df = A_df.loc[sorted_ids, sorted_ids]
                        
                        n = len(A_df)
                        fig_size = max(8, n * 0.8)
                        
                        fig, ax = plt.subplots(figsize=(fig_size, fig_size))
                        sns.heatmap(
                            A_df,
                            annot=True,
                            fmt='.2f',
                            cmap='RdBu_r',
                            vmin=0,
                            vmax=2,
                            square=True,
                            ax=ax,
                            cbar_kws={'label': 'Koefisien Kekerabatan', 'shrink': 0.8},
                            annot_kws={'size': 10}
                        )
                        ax.set_title('Heatmap Matriks Kekerabatan (A)', fontsize=14, fontweight='bold')
                        ax.set_xlabel('ID Individu', fontsize=12)
                        ax.set_ylabel('ID Individu', fontsize=12)
                        plt.xticks(rotation=45, ha='right')
                        plt.yticks(rotation=0)
                        st.pyplot(fig)
                        plt.close(fig)
                    except Exception as e:
                        st.warning(f"⚠️ Tidak dapat menampilkan heatmap: {str(e)}")
            
            # ============================================================
            # DISTRIBUSI NILAI KEKERABATAN
            # ============================================================
            with st.expander("📊 Distribusi Nilai Kekerabatan", expanded=True):
                if st.session_state.results['A'] is not None:
                    try:
                        A_df = st.session_state.results['A']
                        
                        # Urutkan kolom dan index berdasarkan ID
                        sorted_ids = sorted(A_df.index.tolist(), key=natural_sort_key)
                        A_df = A_df.loc[sorted_ids, sorted_ids]
                        
                        values = []
                        for i in range(len(A_df)):
                            for j in range(i+1, len(A_df)):
                                values.append(A_df.iloc[i, j])
                        
                        if values:
                            fig2, ax2 = plt.subplots(figsize=(10, 5))
                            ax2.hist(values, bins=10, edgecolor='black', alpha=0.7, color='skyblue')
                            ax2.axvline(np.mean(values), color='red', linestyle='--', 
                                       label=f'Rata-rata: {np.mean(values):.3f}')
                            ax2.axvline(np.median(values), color='green', linestyle='--', 
                                       label=f'Median: {np.median(values):.3f}')
                            ax2.set_xlabel('Koefisien Kekerabatan', fontsize=12)
                            ax2.set_ylabel('Frekuensi', fontsize=12)
                            ax2.set_title('Distribusi Koefisien Kekerabatan Antar Individu', fontsize=14)
                            ax2.legend()
                            ax2.grid(True, alpha=0.3)
                            st.pyplot(fig2)
                            plt.close(fig2)
                    except Exception as e:
                        st.warning(f"⚠️ Tidak dapat menampilkan distribusi: {str(e)}")
            
            # ============================================================
            # DOWNLOAD HASIL
            # ============================================================
            with st.expander("📥 Download Hasil", expanded=False):
                F_df = pd.DataFrame(
                    st.session_state.results['F'].items(),
                    columns=['ID', 'F']
                )
                
                # Urutkan F_df untuk download
                F_df['_sort_key'] = F_df['ID'].apply(natural_sort_key)
                F_df = F_df.sort_values('_sort_key').drop('_sort_key', axis=1)
                F_df = F_df.reset_index(drop=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    csv_F = F_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Koefisien Inbreeding (CSV)",
                        data=csv_F,
                        file_name='koefisien_inbreeding.csv',
                        mime='text/csv'
                    )
                
                with col2:
                    if st.session_state.results['A'] is not None:
                        A_df = st.session_state.results['A']
                        # Urutkan untuk download
                        sorted_ids = sorted(A_df.index.tolist(), key=natural_sort_key)
                        A_df = A_df.loc[sorted_ids, sorted_ids]
                        csv_A = A_df.to_csv().encode('utf-8')
                        st.download_button(
                            label="📥 Download Matriks A (CSV)",
                            data=csv_A,
                            file_name='matriks_kekerabatan.csv',
                            mime='text/csv'
                        )
    else:
        st.warning("⚠️ Silakan input data silsilah terlebih dahulu di tab '📊 Data Entry'!")

# ================================================================
# MENU: PEDIGREE CHART
# ================================================================
elif menu == "🧬 Pedigree Chart":
    st.markdown("""
    <div class="main-header">
        <h1>🧬 Pedigree Chart - Diagram Silsilah</h1>
        <p>Visualisasi hubungan kekerabatan antar individu dalam bentuk path diagram</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.pedigree is not None:
        df = st.session_state.pedigree
        
        F_dict = st.session_state.results.get('F', None) if 'F' in st.session_state.results else None
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.info(f"📊 Total individu: {len(df)} individu")
            if F_dict:
                st.info(f"📈 Koefisien inbreeding tersedia: {len(F_dict)} individu")
        with col2:
            if st.button("🔄 Refresh Diagram", type="primary"):
                st.rerun()
        
        try:
            G, generations = create_pedigree_chart(df, F_dict)
            
            with st.expander("⚙️ Pengaturan Tampilan", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    show_labels = st.checkbox("Tampilkan Label", value=True)
                with col2:
                    show_inbreeding = st.checkbox("Tampilkan Inbreeding (F)", value=True if F_dict else False)
            
            title = "Pedigree Chart - Silsilah Ternak"
            if F_dict and show_inbreeding:
                title = "Pedigree Chart dengan Koefisien Inbreeding (F)"
            
            fig = draw_pedigree_chart(G, generations, F_dict if show_inbreeding else None, title)
            st.pyplot(fig)
            plt.close(fig)
            
            st.divider()
            st.subheader("📊 Ringkasan Struktur Pedigree")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Jumlah Individu", len(G.nodes))
            with col2:
                st.metric("Jumlah Hubungan", len(G.edges))
            with col3:
                max_gen = max(generations.values()) if generations else 0
                st.metric("Jumlah Generasi", max_gen + 1)
            
            with st.expander("📋 Individu per Generasi"):
                gen_groups = {}
                for node, gen in generations.items():
                    if gen not in gen_groups:
                        gen_groups[gen] = []
                    gen_groups[gen].append(node)
                
                for gen in sorted(gen_groups.keys()):
                    st.write(f"**Generasi {gen}**: {', '.join(sorted(gen_groups[gen]))}")
            
        except Exception as e:
            st.error(f"❌ Error saat membuat diagram: {str(e)}")
            st.info("💡 Pastikan data pedigree memiliki struktur yang valid (induk muncul sebelum anak).")
    else:
        st.warning("⚠️ Silakan input data silsilah terlebih dahulu di tab '📊 Data Entry'!")

# ================================================================
# MENU: CEK PERKAWINAN
# ================================================================
elif menu == "🤝 Cek Perkawinan":
    st.markdown("""
    <div class="main-header">
        <h1>🤝 Cek Perkawinan - Prediksi Inbreeding Anak</h1>
        <p>Evaluasi risiko inbreeding dari perkawinan dua individu</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.pedigree is None:
        st.warning("⚠️ Silakan input data silsilah terlebih dahulu!")
    elif 'F' not in st.session_state.results:
        st.warning("⚠️ Silakan hitung analisis genetika terlebih dahulu di tab '🔬 Analisis'!")
    else:
        df = st.session_state.pedigree
        id_list = df['ID'].tolist()
        A_df = st.session_state.results['A']
        
        st.subheader("📋 Pilih Individu untuk Dikawinkan")
        
        jantan_list = id_list
        betina_list = id_list
        
        if 'SEX' in df.columns:
            df_sex = df['SEX'].astype(str).str.upper().str.strip()
            jantan_mask = df_sex.isin(['M', 'MALE', 'JANTAN', 'J', 'L', 'LAKI', '1'])
            jantan_list = df[jantan_mask]['ID'].tolist()
            betina_mask = df_sex.isin(['F', 'FEMALE', 'BETINA', 'P', 'PEREMPUAN', '2'])
            betina_list = df[betina_mask]['ID'].tolist()
            
            if not jantan_list and not betina_list:
                jantan_list = id_list
                betina_list = id_list
                st.info("💡 Tidak ada data SEX yang valid. Semua individu ditampilkan.")
            else:
                st.info(f"👨 Jantan: {len(jantan_list)} | 👩 Betina: {len(betina_list)}")
        else:
            st.info("💡 Tidak ada kolom SEX. Semua individu ditampilkan.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            sire_options = ['Pilih Sire...'] + jantan_list
            sire_selected = st.selectbox("🔵 Pilih Sire (Jantan)", sire_options)
        
        with col2:
            dam_options = ['Pilih Dam...'] + betina_list
            dam_selected = st.selectbox("🟠 Pilih Dam (Betina)", dam_options)
        
        if st.button("🔍 Cek Perkawinan", type="primary"):
            if sire_selected == 'Pilih Sire...' or dam_selected == 'Pilih Dam...':
                st.warning("⚠️ Silakan pilih Sire dan Dam terlebih dahulu!")
            elif sire_selected == dam_selected:
                st.error("❌ Sire dan Dam tidak boleh sama!")
            else:
                with st.spinner("🔄 Sedang menganalisis..."):
                    result = cek_perkawinan(sire_selected, dam_selected, A_df, id_list)
                
                if "error" in result:
                    st.error(f"❌ {result['error']}")
                else:
                    st.divider()
                    st.subheader("📊 Hasil Analisis Perkawinan")
                    
                    color = result['color']
                    status = result['status']
                    F_anak = result['F_anak']
                    
                    if color == "green":
                        st.success(f"### {status}")
                    elif color in ["lightgreen"]:
                        st.info(f"### {status}")
                    elif color in ["orange", "yellow"]:
                        st.warning(f"### {status}")
                    else:
                        st.error(f"### {status}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("👨 Sire", result['sire_id'])
                    with col2:
                        st.metric("👩 Dam", result['dam_id'])
                    with col3:
                        st.metric("🧬 Inbreeding Anak (F)", f"{F_anak:.4f}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Kekerabatan Sire-Dam", f"{result['a_sire_dam']:.4f}")
                    with col2:
                        st.metric("Inbreeding Sire", f"{result['F_sire']:.4f}")
                    
                    st.info(f"💡 {result['detail']}")
                    
                    if result['hubungan']:
                        st.warning("⚠️ Hubungan Kekerabatan Terdeteksi:")
                        for h in result['hubungan']:
                            st.write(f"  - {h}")
                    else:
                        st.success("✅ Tidak ada hubungan kekerabatan langsung.")
                    
                    st.divider()
                    st.subheader("📋 Rekomendasi")
                    
                    if F_anak == 0:
                        st.success("✅ **PERKAWINAN AMAN** - Tidak ada risiko inbreeding.")
                    elif F_anak < 0.0625:
                        st.info("🟢 **PERKAWINAN DAPAT DIPERTIMBANGKAN** - Risiko inbreeding sangat rendah.")
                    elif F_anak < 0.125:
                        st.warning("🟡 **PERKAWINAN DENGAN CATATAN** - Terdapat risiko inbreeding sedang.")
                    elif F_anak < 0.25:
                        st.error("🟠 **PERKAWINAN TIDAK DISARANKAN** - Risiko inbreeding tinggi!")
                    else:
                        st.error("🔴 **PERKAWINAN HARUS DIHINDARI!** - Risiko inbreeding sangat ekstrem!")
                    
                    with st.expander("📊 Lihat Posisi dalam Matriks Kekerabatan"):
                        st.write(f"**Koefisien kekerabatan antara {sire_selected} dan {dam_selected}: {result['a_sire_dam']:.4f}**")
                        subset_cols = [sire_selected, dam_selected]
                        subset_df = A_df.loc[subset_cols, subset_cols]
                        st.dataframe(subset_df.style.background_gradient(cmap='Blues', axis=None))

# ================================================================
# MENU: LAPORAN
# ================================================================
elif menu == "📈 Laporan":
    st.markdown("""
    <div class="main-header">
        <h1>📈 Ekspor Laporan</h1>
        <p>Download hasil analisis dalam format CSV</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.pedigree is not None:
        st.subheader("📄 Ringkasan Data")
        
        df = st.session_state.pedigree
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Individu", len(df))
        with col2:
            known_sire = sum(df['Sire'] != '0')
            st.metric("Sire Diketahui", f"{known_sire} ({known_sire/len(df)*100:.1f}%)")
        with col3:
            known_dam = sum(df['Dam'] != '0')
            st.metric("Dam Diketahui", f"{known_dam} ({known_dam/len(df)*100:.1f}%)")
        
        if 'F' in st.session_state.results:
            st.divider()
            st.subheader("📥 Download Hasil Analisis")
            
            F_df = pd.DataFrame(
                st.session_state.results['F'].items(),
                columns=['ID', 'F']
            )
            
            col1, col2 = st.columns(2)
            with col1:
                csv_F = F_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Koefisien Inbreeding (CSV)",
                    data=csv_F,
                    file_name='koefisien_inbreeding.csv',
                    mime='text/csv'
                )
            
            with col2:
                if st.session_state.results['A'] is not None:
                    csv_A = st.session_state.results['A'].to_csv().encode('utf-8')
                    st.download_button(
                        label="📥 Download Matriks A (CSV)",
                        data=csv_A,
                        file_name='matriks_kekerabatan.csv',
                        mime='text/csv'
                    )
    else:
        st.info("📌 Input data terlebih dahulu untuk membuat laporan")
