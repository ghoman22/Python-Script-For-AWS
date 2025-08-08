# 🌐 Tool Ngatur IP Elastic AWS 

Tool keren pake bahasa Jakarta asli buat ngatur-ngatur alamat IP Elastic AWS dengan tampilan console yang cakep dan fitur yang mantap!

## ✨ Fitur yang Kece

### 🎯 Fungsi Utama
- **Deteksi EIP Pinter**: Otomatis tau mana IP yang udah nempel sama yang masih nganggur
- **Mode Operasi Macem-macem**: Mode interaktif, batch, sama dry-run
- **Analisis Biaya**: Hitungan biaya real-time dan estimasi penghematan
- **Keamanan Utama**: Validasi komprehensif sama konfirmasi yang oke

### 🎨 Pengalaman User
- **Output Console yang Cakep**: Tabel cantik, progress bar, sama warna-warni
- **Prompt Interaktif**: Konfirmasi yang user-friendly pake Rich UI
- **Indikator Progress**: Tracking visual buat operasi batch
- **Logging Professional**: Enhanced logging dengan timestamp dan formatting

### 🔧 Fitur Advanced
- **Support Profile AWS**: Bisa kerja sama profile AWS macem-macem
- **Support Multi-Region**: Operasi di region AWS yang beda-beda
- **Generate Laporan**: Ekspor laporan detail format JSON
- **Tracking Statistik**: Statistik operasi yang lengkap
- **Error Handling**: Error handling yang robust dengan pesan yang helpful

## 📋 Requirements

- Python 3.7+
- AWS CLI udah dikonfigurasi atau environment variables udah diset
- Package Python yang dibutuhin (liat requirements.txt)

## 🚀 Instalasi

1. **Clone atau download scriptnya**
2. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```
3. **Bikin script executable (Linux/Mac):**
   ```bash
   chmod +x delete_elastic_ip.py
   ```

## 🔑 Konfigurasi AWS

Pastiin kredensial AWS udah dikonfigurasi pake salah satu cara ini:

### Opsi 1: AWS CLI
```bash
aws configure
```

### Opsi 2: Environment Variables
```bash
export AWS_ACCESS_KEY_ID="access_key_lu"
export AWS_SECRET_ACCESS_KEY="secret_key_lu"
export AWS_DEFAULT_REGION="us-east-1"
```

### Opsi 3: IAM Roles (buat instance EC2)
Attach IAM role yang punya permission yang tepat ke instance EC2 lu.

## 📖 Cara Pake

### Penggunaan Dasar

```bash
# Mode interaktif (default) - review tiap EIP satu-satu
python3 delete_elastic_ip.py

# Dry run - liat apa yang bakal dibuang tanpa beneran buang
python3 delete_elastic_ip.py --dry-run

# Mode batch - buang semua EIP nganggur dengan konfirmasi
python3 delete_elastic_ip.py --batch

# Mode batch dengan auto-konfirmasi (bahaya!)
python3 delete_elastic_ip.py --batch --yes
```

### Penggunaan Advanced

```bash
# Pake profile AWS tertentu
python3 delete_elastic_ip.py --profile production

# Pake region tertentu
python3 delete_elastic_ip.py --region us-west-2

# Generate laporan detail
python3 delete_elastic_ip.py --export-report

# Kombinasi opsi
python3 delete_elastic_ip.py --profile prod --region eu-west-1 --dry-run --export-report
```

## 🎛️ Opsi Command Line

| Opsi | Pendek | Deskripsi |
|------|--------|-----------|
| `--dry-run` | `-d` | Mode preview - cuma liat apa yang bakal dibuang |
| `--interactive` | `-i` | Mode interaktif (default) |
| `--batch` | `-b` | Mode batch - buang semua EIP nganggur |
| `--profile` | `-p` | Profile AWS yang mau dipake |
| `--region` | `-r` | Region AWS yang mau dioperasiin |
| `--yes` | `-y` | Skip konfirmasi |
| `--export-report` | `-e` | Ekspor laporan detail JSON |
| `--report-file` | | Nama file custom buat laporan |
| `--version` | `-v` | Info versi |
| `--help` | `-h` | Pesan bantuan |

## 🎯 Mode Operasi

### 1. Mode Interaktif (Default)
- Review tiap EIP nganggur satu-satu
- Bikin keputusan yang informed dengan informasi detail
- Operasi yang aman dan terkontrol

### 2. Mode Dry Run
- Preview apa yang bakal dibuang
- Analisis dampak biaya
- Perfect buat planning dan validasi

### 3. Mode Batch
- Buang semua EIP nganggur sekaligus
- Progress bar buat feedback visual
- Konfirmasi opsional buat automasi

## 💰 Analisis Biaya

Tool ini kasih analisis biaya real-time:
- **EIP yang Nempel**: $0.00/bulan (gratis kalo udah nempel)
- **EIP Nganggur**: $3.65/bulan per IP
- **Kalkulasi Otomatis**: Proyeksi biaya bulanan dan tahunan

## 📊 Contoh Output

### Tabel Ringkasan yang Cakep
```
┌─────────────────┬──────────────────────┬──────────┬─────────────┬────────┬──────────────┐
│ Alamat IP       │ ID Alokasi           │ Status   │ Instance/ENI│ Domain │ Biaya Bulanan│
├─────────────────┼──────────────────────┼──────────┼─────────────┼────────┼──────────────┤
│ 203.0.113.1     │ eipalloc-12345678... │ ✓ Nempel │ i-1234567890│ vpc    │ $0.00        │
│ 203.0.113.2     │ eipalloc-87654321... │ ✗ Nganggu│ Kosong      │ vpc    │ $3.65        │
└─────────────────┴──────────────────────┴──────────┴─────────────┴────────┴──────────────┘
```

### Panel Dampak Biaya
```
╭─────────── Dampak Finansial ────────────╮
│ 💰 Dampak Biaya                         │
│                                         │
│ EIP yang nganggur: 3                    │
│ Buang duit bulanan: $10.95              │
│ Buang duit tahunan: $131.40             │
╰─────────────────────────────────────────╯
```

## 📄 Generate Laporan

Generate laporan JSON detail dengan:
```bash
python3 delete_elastic_ip.py --export-report
```

Laporan include:
- Timestamp dan konfigurasi
- Informasi EIP yang detail
- Statistik operasi
- Analisis biaya

## ⚠️ Fitur Keamanan

1. **Prompt Konfirmasi**: Beberapa step konfirmasi
2. **Mode Dry Run**: Test tanpa bikin perubahan
3. **Logging Detail**: Track semua operasi
4. **Error Handling**: Recovery error yang graceful
5. **Validasi**: Pre-flight check buat koneksi AWS

## 🛡️ Permission IAM yang Dibutuhin

User/role AWS lu butuh permission ini:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeAddresses",
                "ec2:ReleaseAddress",
                "ec2:DescribeRegions"
            ],
            "Resource": "*"
        }
    ]
}
```

## 🐛 Troubleshooting

### Masalah yang Sering

1. **Error Kredensial AWS**
   ```
   Solusi: Konfigurasi kredensial AWS pake aws configure
   ```

2. **Permission Denied**
   ```
   Solusi: Pastiin IAM user punya permission EC2 yang dibutuhin
   ```

3. **Module Not Found**
   ```
   Solusi: Install requirements: pip install -r requirements.txt
   ```

4. **Region Not Found**
   ```
   Solusi: Specify region AWS yang valid pake flag --region
   ```

## 🔄 Riwayat Versi

- **v2.0.0 Edisi Betawi**: Rewrite lengkap pake rich UI dan bahasa Betawi
- **v1.0.0**: Fungsionalitas dasar

## 📝 Lisensi

Tool ini disediain as-is buat keperluan edukasi dan operasional.

## ⚡ Quick Start

1. Install dependencies: `pip3 install -r requirements.txt`
2. Konfigurasi AWS: `aws configure`
3. Jalanin dry run: `python3 delete_elastic_ip.py --dry-run`
4. Jalanin interaktif: `python3 delete_elastic_ip.py`

---

**⚠️ Selalu test pake --dry-run dulu, Bos!**

*Tool ini dibuat pake cinta dan semangat Jakarta! 🏙️*