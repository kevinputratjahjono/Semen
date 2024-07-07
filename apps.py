import streamlit as st
from datetime import datetime
import pandas as pd
from web3 import Web3

# Set page configuration
st.set_page_config(
    page_title="Aplikasi Manajemen Stok Semen",
    page_icon=":truck:",  # You can use emojis here
    layout="wide"
)

# Set up a nice background color and font
st.markdown(
    """
    <style>
    body {
        background-color: #f0f2f6;
        color: #333333;
        font-family: 'Arial', sans-serif;
    }
    .stButton>button {
        background-color: #3366ff;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        text-align: center;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #254eda;
    }
    .stTextInput > div > div > input {
        color: white !important; /* Ubah warna tulisan menjadi putih */
    }
    .stNumberInput > div > div > input {
        color: #333333 !important;
    }
    .stDateInput > div > div > input {
        color: #333333 !important;
    }
    .sidebar .sidebar-content {
        background-color: white;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-radius: 0.75rem;
        padding: 1rem;
        z-index: 1; /* Ensure sidebar is on top */
        position: relative;
    }
    .sidebar .sidebar-content .stSelectbox > div > div > div {
        color: #333333 !important;
    }
    .sidebar .sidebar-content .stSelectbox > div > div > div > div {
        color: #333333 !important;
    }
    .st-ux .st-dm .st-cl {
        background: white !important;
    }
    .stDateInput .st-ax {
        z-index: 1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if 'stok_semen' not in st.session_state:
    st.session_state.stok_semen = 0
if 'penjualan' not in st.session_state:
    st.session_state.penjualan = []

# Web3 configuration
blockchain_url = 'http://127.0.0.1:8545'  # Ganache URL
web3 = Web3(Web3.HTTPProvider(blockchain_url))

# Set the default account to use for transactions
web3.eth.default_account = web3.eth.accounts[0]

# Load Smart Contract ABI and Address (example)
contract_address = '0xd60Db1694af09e5c1826F5d7C0099455fEF5c73D'  # Update with your smart contract address
contract_abi = [
    {
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "recordSale",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Sidebar menu
st.sidebar.title('Menu')
menu = st.sidebar.selectbox('Pilih Menu', ['Penjualan Semen', 'Stok Semen', 'Laporan Penjualan'])

# Main content based on menu selection
if menu == 'Penjualan Semen':
    st.title('Aplikasi Manajemen Penjualan Semen')

    # Display current stock
    st.subheader('Stok Semen Saat Ini')
    st.write(f'Stok semen: {st.session_state.stok_semen} sak')

    # User inputs
    st.subheader('Form Penjualan Semen')
    harga_per_sak = 65000  # Fixed price per sak
    jumlah_sak = st.number_input('Jumlah sak yang terjual', min_value=0, value=0, step=1, max_value=st.session_state.stok_semen)
    tanggal_penjualan = st.date_input('Tanggal penjualan', value=datetime.today())
    nama_pembeli = st.text_input('Nama pembeli')

    # Calculate total sales
    total_penjualan = harga_per_sak * jumlah_sak

    # Display result
    st.subheader('Total Penjualan')
    st.write(f'Rp {total_penjualan:,}')

    # Save sales data
    if st.button('Simpan Penjualan'):
        if jumlah_sak <= st.session_state.stok_semen:
            # Save transaction data to smart contract
            try:
                tx_hash = contract.functions.recordSale(jumlah_sak).transact({'from': web3.eth.default_account})
                st.session_state.penjualan.append({
                    'harga': harga_per_sak,
                    'jumlah': jumlah_sak,
                    'total': total_penjualan,
                    'tanggal': tanggal_penjualan,
                    'pembeli': nama_pembeli
                })
                st.session_state.stok_semen -= jumlah_sak
                st.success('Data penjualan berhasil disimpan dan dicatat di smart contract!')

            except Exception as e:
                st.error(f'Gagal menyimpan data penjualan di smart contract: {str(e)}')

        else:
            st.error('Jumlah sak yang terjual melebihi stok yang tersedia.')

    # Display sales history
    st.subheader('Riwayat Penjualan')
    if st.session_state.penjualan:
        penjualan_df = pd.DataFrame(st.session_state.penjualan)
        st.dataframe(penjualan_df)

    else:
        st.info('Belum ada data penjualan.')

elif menu == 'Stok Semen':
    st.title('Manajemen Stok Semen')

    # User input for stock
    st.subheader('Update Stok Semen')
    stok_masuk = st.number_input('Jumlah sak semen masuk', min_value=0, value=0, step=1)

    # Update stock
    if st.button('Update Stok'):
        st.session_state.stok_semen += stok_masuk
        st.success('Stok semen berhasil diperbarui!')

    # Display current stock
    st.subheader('Stok Semen Saat Ini')
    st.write(f'Stok semen: {st.session_state.stok_semen} sak')

elif menu == 'Laporan Penjualan':
    st.title('Laporan Penjualan Semen')

    # Display sales report
    st.subheader('Data Laporan Penjualan')
    if st.session_state.penjualan:
        penjualan_df = pd.DataFrame(st.session_state.penjualan)
        st.dataframe(penjualan_df)

        # Search and filter
        st.subheader('Pencarian dan Filter')
        search_query = st.text_input('Cari berdasarkan nama pembeli')
        filtered_df = penjualan_df[penjualan_df['pembeli'].str.contains(search_query, case=False)]
        st.dataframe(filtered_df)

        # Export data
        st.subheader('Ekspor Data')
        if st.button('Unduh Data Penjualan'):
            csv = penjualan_df.to_csv(index=False)
            st.download_button(label='Unduh CSV', data=csv, file_name='penjualan_semen.csv', mime='text/csv')

    else:
        st.info('Belum ada data penjualan.')
