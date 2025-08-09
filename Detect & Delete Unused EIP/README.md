# 🚀 AWS Resource Management Tools 

Kumpulan tool keren buat ngatur-ngatur AWS resources dengan hemat biaya maksimal!

## 📁 Daftar Tools

### 1. 🌐 delete_elastic_ip.py
Tool spesialis buat ngatur Elastic IP dengan fitur mantap:
- **Focus**: Elastic IP management only
- **Features**: Interactive, batch, dry-run modes
- **Display**: Beautiful tables dengan cost analysis
- **Safety**: Comprehensive error handling

### 2. 🚀 aws_resource_cleaner.py (NEW!)
Tool comprehensive buat ngatur berbagai unused AWS resources sekaligus:
- **Focus**: Multiple resource types dalam satu tool
- **Resource Types**: EIP, ELB, EBS, Snapshots, RDS, NAT Gateway, ENI
- **Features**: Interactive resource selection + all modes dari script lama
- **Display**: Tree view yang cakep + detailed cost analysis

---

## 🎯 AWS Resource Cleaner Comprehensive

**Script baru yang lebih powerful untuk mengelola berbagai unused AWS resources sekaligus!**

### 📋 Resource Types yang Didukung

| Icon | Resource Type | Description | Est. Cost/Month |
|------|---------------|-------------|-----------------|
| 🌐 | **Elastic IP (EIP)** | IP yang tidak attached ke instance/ENI | $3.65 |
| ⚖️ | **Elastic Load Balancer** | Load balancer tanpa healthy targets | $22.50 |
| 💾 | **EBS Volumes** | Volume yang tidak attached | $10.00/100GB |
| 📸 | **EBS Snapshots** | Snapshot lama (>30 hari) tanpa AMI | $5.00/100GB |
| 🗄️ | **RDS Instances** | Database instance yang stopped/idle | $50.00+ |
| 🚪 | **NAT Gateways** | NAT Gateway tanpa routes aktif | $32.85 |
| 🔌 | **Network Interfaces** | ENI yang tidak attached | $1.00 |

### 🎯 Fitur Utama

- ✅ **Interactive Resource Selection** - Pilih resource types yang mau dicek
- ✅ **Multiple Operation Modes** - Dry run, Interactive, dan Batch
- ✅ **Cost Analysis** - Estimate penghematan biaya bulanan/tahunan
- ✅ **Beautiful Display** - Tree view dan tabel yang cakep dengan Rich
- ✅ **Comprehensive Reporting** - Export laporan detail ke JSON
- ✅ **Safety First** - Dry run mode dan konfirmasi sebelum delete
- ✅ **Multi-profile Support** - Support berbagai AWS profiles dan regions

### 🔧 Installation & Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Setup AWS credentials (pilih salah satu)
aws configure                    # Setup default profile
aws configure --profile prod    # Setup named profile

# Test koneksi
python3 aws_resource_cleaner.py --help
```

### 🎮 Quick Start Guide

#### 1. **Safety First - Dry Run** (Recommended untuk pertama kali)
```bash
python3 aws_resource_cleaner.py --dry-run
```
Preview semua unused resources tanpa hapus apa-apa. **100% SAFE!**

#### 2. **Interactive Mode** (Recommended untuk daily use)
```bash
python3 aws_resource_cleaner.py --interactive
```
Script akan:
1. Tampilkan menu pilihan resource types
2. Scan resources yang dipilih
3. Konfirmasi manual per resource sebelum delete

#### 3. **Targeted Cleanup** (Pilih resource types spesifik)
```bash
# Cuma scan EIP dan EBS volumes
python3 aws_resource_cleaner.py --resources eip,ebs --interactive

# Scan semua kecuali RDS (safety first!)
python3 aws_resource_cleaner.py --resources eip,elb,ebs,snapshot,nat,eni --dry-run
```

#### 4. **Multi-environment Support**
```bash
# Production account di Singapore
python3 aws_resource_cleaner.py --profile production --region ap-southeast-1 --dry-run

# Development account dengan cleanup batch
python3 aws_resource_cleaner.py --profile dev --region us-west-2 --resources eip,ebs --batch
```

#### 5. **Batch Mode** (Dangerous but efficient)
```bash
# Dengan konfirmasi
python3 aws_resource_cleaner.py --batch

# Auto-confirm (VERY DANGEROUS!)
python3 aws_resource_cleaner.py --batch --yes
```

#### 6. **Generate Reports**
```bash
# Export ke file default
python3 aws_resource_cleaner.py --dry-run --export-report

# Export ke file custom
python3 aws_resource_cleaner.py --dry-run --export-report --report-file monthly_cleanup.json
```

### 📊 Sample Output

```
🗂️ Unused AWS Resources
├── 🌐 Elastic IP (3 items, $10.95/month)
│   ├── IP: 52.74.123.456 ($3.65/month)
│   ├── IP: 13.250.987.654 ($3.65/month)
│   └── IP: 18.142.555.777 ($3.65/month)
├── 💾 EBS Volumes (2 items, $12.00/month)
│   ├── Volume: vol-0123456789abcdef0 (100GB, $8.00/month)
│   └── Volume: vol-0987654321fedcba0 (50GB, $4.00/month)
└── 📸 EBS Snapshots (5 items, $15.50/month)
    ├── Snapshot: snap-0111222333444555 (20GB, $1.00/month)
    └── ... dan 4 lainnya

┌─────────────────────────────────────────────────────────────┐
│                        💰 Cost Impact                       │
├─────────────────────────────────────────────────────────────┤
│ Summary                                                     │
│                                                             │
│ Total unused resources: 10                                  │
│ Estimated monthly cost: $38.45                             │
│ Potential yearly savings: $461.40                          │
└─────────────────────────────────────────────────────────────┘
```

### 📋 All Available Commands

```bash
# Basic modes
--dry-run, -d           # Preview mode (SAFE)
--interactive, -i       # Interactive confirmation
--batch, -b            # Batch delete mode

# Resource selection
--resources eip,ebs    # Specific resource types
                       # Available: eip,elb,ebs,snapshot,rds,nat,eni

# AWS configuration  
--profile PROFILE      # AWS profile name
--region REGION        # AWS region

# Additional options
--yes, -y             # Skip confirmations (use with --batch)
--export-report, -e   # Generate JSON report
--report-file FILE    # Custom report filename
--version, -v         # Show version
--help, -h           # Show help
```

### ⚠️ Safety Guidelines

| ⚠️ **CRITICAL SAFETY NOTES** |
|------------------------------|
| 1. **Always start with `--dry-run`** untuk familiarize dengan output |
| 2. **Backup important data** sebelum delete RDS instances |
| 3. **Check resource dependencies** - some resources might still be needed |
| 4. **Test di development environment** dulu sebelum production |
| 5. **RDS deletion is PERMANENT** - no easy recovery! |

### 🆚 Script Comparison

| Feature | delete_elastic_ip.py | aws_resource_cleaner.py |
|---------|---------------------|-------------------------|
| **Resource Types** | EIP only | 7 types (EIP, ELB, EBS, RDS, dll) |
| **Resource Selection** | N/A | Interactive menu |
| **Cost Analysis** | EIP only ($3.65/month) | All types with real pricing |
| **Display** | Tables | Tree view + tables |
| **Reporting** | Basic statistics | Comprehensive JSON export |
| **Use Case** | EIP-specific cleanup | Comprehensive AWS cleanup |
| **Learning Curve** | Simple | Medium |

### 🎯 Which Tool to Use?

- **Use `delete_elastic_ip.py`** when:
  - You only need to clean up Elastic IPs
  - You want a simple, focused tool
  - You're learning AWS resource management

- **Use `aws_resource_cleaner.py`** when:
  - You want comprehensive AWS cleanup
  - You manage multiple resource types
  - You need detailed cost analysis
  - You want advanced reporting features

### 💡 Pro Tips

1. **Start Small**: Begin dengan `--resources eip,eni` yang relatif safe
2. **Regular Cleanup**: Run weekly dengan `--dry-run` untuk monitoring
3. **Automation**: Consider setting up scheduled runs dengan cron
4. **Team Usage**: Share reports untuk visibility across team
5. **Cost Optimization**: Focus pada high-cost resources seperti NAT Gateway dan RDS

### 🔮 Coming Soon

- Support untuk CloudWatch Logs, Security Groups, Key Pairs
- Integration dengan AWS Cost Explorer API
- Slack/Email notifications untuk scheduled runs
- Lambda deployment untuk serverless cleanup
- Dashboard web untuk team collaboration

### 📞 Need Help?

```bash
# Show help untuk specific tool
python3 aws_resource_cleaner.py --help
python3 delete_elastic_ip.py --help

# Test basic functionality
python3 aws_resource_cleaner.py --version
```

---

## 🏆 Best Practices

### For Beginners:
1. Start dengan `aws_resource_cleaner.py --dry-run`
2. Use `--interactive` mode untuk learning
3. Focus pada safe resources (EIP, ENI) dulu

### For Advanced Users:
1. Use `--batch` mode dengan specific `--resources`
2. Setup multiple profiles untuk different environments  
3. Automate dengan cron + `--export-report`

### For Teams:
1. Share JSON reports untuk transparency
2. Use consistent profiles dan naming
3. Document cleanup schedules dan procedures

---

**Selamat berhemat dan AWS account yang bersih, Bos! 💰✨**

