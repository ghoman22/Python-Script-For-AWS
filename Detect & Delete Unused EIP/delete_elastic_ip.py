#!/usr/bin/env python3
"""
Tool Ngatur Elastic IP AWS Pake Bahasa Betawi
===========================================

Tool keren buat ngatur-ngatur IP Elastic AWS dengan fitur mantap:
- Mode interaktif sama batch buat apus-apus IP
- Tampilan console yang cakep pake warna-warni
- Error handling yang komprehensif dan logging yang oke
- Fitur dry-run buat nyoba-nyoba tanpa takut rusak
- Laporan detail dan statistik yang kece

Pembuat: Tim DevOps yang Kece
Versi: 2.0.0 Edisi Betawi
"""

import argparse
import boto3
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import colorama
from botocore.exceptions import (
    BotoCoreError, ClientError, NoCredentialsError,
    PartialCredentialsError, ProfileNotFound
)
from colorama import Fore, Back, Style
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.logging import RichHandler
from rich.text import Text

# Initialize colorama buat warna-warni cross-platform
colorama.init(autoreset=True)

# Initialize Rich console
console = Console()


class ManagerElasticIPBetawi:
    """Kelas Manager IP Elastic AWS yang Kece Pake Bahasa Betawi"""

    def __init__(self, profile: Optional[str] = None, region: Optional[str] = None):
        """
        Inisialisasi Manager Elastic IP

        Args:
            profile: Profile AWS yang mau dipake
            region: Region AWS yang mau dioperasiin
        """
        self.profile = profile
        self.region = region or os.environ.get(
            'AWS_DEFAULT_REGION', 'us-east-1')
        self.ec2_client = None
        self.session = None
        self.statistik = {
            'total_eips': 0,
            'eips_nempel': 0,
            'eips_nganggur': 0,
            'eips_dibuang': 0,
            'gagal_buang': 0,
            'hemat_duit': 0.0
        }

        self._setup_logging()
        self._inisialisasi_client_aws()

    def _setup_logging(self) -> None:
        """Setup logging yang kece pake Rich handler"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(console=console, rich_tracebacks=True)]
        )
        self.logger = logging.getLogger("Manager_EIP_Betawi")

    def _inisialisasi_client_aws(self) -> None:
        """Inisialisasi client AWS dengan error handling yang mantap"""
        try:
            # Bikin session pake profile kalo ada
            if self.profile:
                self.session = boto3.Session(profile_name=self.profile)
                console.print(
                    f"[green]✓[/green] Pake profile AWS: [bold cyan]{self.profile}[/bold cyan]")
            else:
                self.session = boto3.Session()
                console.print(
                    "[green]✓[/green] Pake kredensial AWS default nih")

            # Inisialisasi client EC2
            self.ec2_client = self.session.client(
                'ec2', region_name=self.region)

            # Test kredensial dengan panggil API sederhana
            self.ec2_client.describe_regions(RegionNames=[self.region])
            console.print(
                f"[green]✓[/green] Udah konek ke region AWS: [bold cyan]{self.region}[/bold cyan]")

        except ProfileNotFound as e:
            console.print(
                f"[red]✗[/red] Profile AWS '{self.profile}' kagak ketemu, Bos!")
            sys.exit(1)
        except (NoCredentialsError, PartialCredentialsError):
            console.print(
                "[red]✗[/red] Kredensial AWS kagak ada atau kurang lengkap nih!")
            console.print("Tolong setting kredensial AWS pake:")
            console.print("  • aws configure")
            console.print(
                "  • Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)")
            console.print("  • IAM roles (buat instance EC2)")
            sys.exit(1)
        except ClientError as e:
            console.print(f"[red]✗[/red] Error konek ke AWS: {e}")
            sys.exit(1)

    def ambil_elastic_ips(self) -> List[Dict]:
        """
        Ambil semua alamat IP Elastic di akun

        Returns:
            List dictionary IP Elastic
        """
        try:
            with console.status("[bold green]Lagi ngecek IP Elastic..."):
                response = self.ec2_client.describe_addresses()
                eips = response.get('Addresses', [])

            self.statistik['total_eips'] = len(eips)

            # Kategorikan EIP
            for eip in eips:
                if self._cek_eip_nempel(eip):
                    self.statistik['eips_nempel'] += 1
                else:
                    self.statistik['eips_nganggur'] += 1

            console.print(f"[green]✓[/green] Ketemu {len(eips)} IP Elastic")
            return eips

        except ClientError as e:
            self.logger.error(f"Gagal ambil IP Elastic: {e}")
            return []

    def _cek_eip_nempel(self, eip: Dict) -> bool:
        """
        Cek apakah EIP udah nempel ke instance atau network interface

        Args:
            eip: Dictionary EIP dari API AWS

        Returns:
            True kalo udah nempel, False kalo belum
        """
        return bool(eip.get('InstanceId') or eip.get('NetworkInterfaceId'))

    def tampilkan_ringkasan_eip(self, eips: List[Dict]) -> None:
        """Tampilkan tabel ringkasan IP Elastic yang cakep"""
        if not eips:
            console.print(
                "[yellow]⚠[/yellow] Kagak ada IP Elastic di region ini, Bos!")
            return

        # Bikin tabel ringkasan
        table = Table(title="🌐 Ringkasan Alamat IP Elastic",
                      show_header=True, header_style="bold magenta")
        table.add_column("Alamat IP", style="cyan", no_wrap=True)
        table.add_column("ID Alokasi", style="dim")
        table.add_column("Status", justify="center")
        table.add_column("Instance/ENI", style="green")
        table.add_column("Domain", justify="center")
        table.add_column("Biaya Bulanan", style="yellow", justify="right")

        jumlah_nganggur = 0
        for eip in eips:
            ip_publik = eip.get('PublicIp', 'Kagak Ada')
            id_alokasi = eip.get('AllocationId', 'Kagak Ada')
            domain = eip.get('Domain', 'classic')

            if self._cek_eip_nempel(eip):
                status = "[green]✓ Udah Nempel[/green]"
                resource = eip.get('InstanceId') or eip.get(
                    'NetworkInterfaceId', 'Kagak Ada')
                biaya = "[dim]$0.00[/dim]"
            else:
                status = "[red]✗ Nganggur[/red]"
                resource = "[dim]Kosong[/dim]"
                # Biaya EIP AWS per bulan kalo nganggur
                biaya = "[yellow]$3.65[/yellow]"
                jumlah_nganggur += 1

            table.add_row(
                ip_publik, id_alokasi[:20] + "...", status, resource, domain, biaya)

        console.print(table)

        # Tampilkan ringkasan biaya
        if jumlah_nganggur > 0:
            buang_duit_bulanan = jumlah_nganggur * 3.65
            buang_duit_tahunan = buang_duit_bulanan * 12
            self.statistik['hemat_duit'] = buang_duit_bulanan

            panel_biaya = Panel(
                f"[red]💰 Dampak Biaya[/red]\n\n"
                f"EIP yang nganggur: [bold red]{jumlah_nganggur}[/bold red]\n"
                f"Buang duit bulanan: [bold yellow]${buang_duit_bulanan:.2f}[/bold yellow]\n"
                f"Buang duit tahunan: [bold red]${buang_duit_tahunan:.2f}[/bold red]",
                title="Dampak Finansial",
                border_style="red"
            )
            console.print(panel_biaya)

    def buang_eip(self, allocation_id: str, ip_publik: str) -> bool:
        """
        Buang IP Elastic yang spesifik

        Args:
            allocation_id: ID alokasi dari EIP
            ip_publik: Alamat IP publik (buat logging)

        Returns:
            True kalo berhasil, False kalo gagal
        """
        try:
            self.ec2_client.release_address(AllocationId=allocation_id)
            console.print(
                f"[green]✓[/green] Berhasil buang EIP: [bold]{ip_publik}[/bold] ({allocation_id})")
            self.statistik['eips_dibuang'] += 1
            return True

        except ClientError as e:
            kode_error = e.response.get('Error', {}).get('Code', 'Kagak Tau')
            console.print(
                f"[red]✗[/red] Gagal buang {ip_publik}: {kode_error}")
            self.logger.error(f"Gagal buang EIP {allocation_id}: {e}")
            self.statistik['gagal_buang'] += 1
            return False

    def mode_interaktif(self, eips: List[Dict]) -> None:
        """Mode interaktif buat buang EIP satu-satu"""
        console.print("\n[bold blue]🎯 Mode Interaktif[/bold blue]")
        console.print(
            "Review tiap EIP yang nganggur terus pilih mau dibuang atau kagak.\n")

        eips_nganggur = [eip for eip in eips if not self._cek_eip_nempel(eip)]

        if not eips_nganggur:
            console.print(
                "[green]✨[/green] Semua IP Elastic udah nempel dengan baik!")
            return

        for i, eip in enumerate(eips_nganggur, 1):
            ip_publik = eip.get('PublicIp', 'Kagak Ada')
            allocation_id = eip.get('AllocationId', 'Kagak Ada')

            console.print(f"\n[bold]EIP {i}/{len(eips_nganggur)}:[/bold]")
            console.print(f"  Alamat IP: [cyan]{ip_publik}[/cyan]")
            console.print(f"  ID Alokasi: [dim]{allocation_id}[/dim]")
            console.print(f"  Biaya Bulanan: [yellow]$3.65[/yellow]")

            if Confirm.ask(f"  Mau buang EIP ini, Bos?", default=False):
                self.buang_eip(allocation_id, ip_publik)
            else:
                console.print(f"  [dim]Dilewatin deh {ip_publik}[/dim]")

    def mode_batch(self, eips: List[Dict], konfirmasi: bool = True) -> None:
        """Mode batch buat buang semua EIP yang nganggur"""
        eips_nganggur = [eip for eip in eips if not self._cek_eip_nempel(eip)]

        if not eips_nganggur:
            console.print(
                "[green]✨[/green] Semua IP Elastic udah nempel dengan baik!")
            return

        console.print(f"\n[bold red]🔥 Mode Batch[/bold red]")
        console.print(
            f"Ketemu [bold]{len(eips_nganggur)}[/bold] EIP yang nganggur")

        if konfirmasi:
            hemat_biaya = len(eips_nganggur) * 3.65
            if not Confirm.ask(
                f"Buang SEMUA {len(eips_nganggur)} EIP yang nganggur? "
                f"(Ini bisa hemat ${hemat_biaya:.2f}/bulan lho!)",
                default=False
            ):
                console.print("[yellow]⚠[/yellow] Operasi batch dibatalin")
                return

        # Buang EIP pake progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:

            task = progress.add_task(
                "Lagi buang EIP...", total=len(eips_nganggur))

            for eip in eips_nganggur:
                allocation_id = eip.get('AllocationId', 'Kagak Ada')
                ip_publik = eip.get('PublicIp', 'Kagak Ada')

                self.buang_eip(allocation_id, ip_publik)
                progress.advance(task)
                time.sleep(0.5)  # Delay dikit biar kagak kena rate limiting

    def mode_dry_run(self, eips: List[Dict]) -> None:
        """Mode dry run - cuma liat apa yang bakal dibuang tanpa beneran buang"""
        console.print("\n[bold yellow]🧪 Mode Dry Run[/bold yellow]")
        console.print(
            "Analisis apa yang bakal dibuang (kagak bakal ada perubahan beneran)\n")

        eips_nganggur = [eip for eip in eips if not self._cek_eip_nempel(eip)]

        if not eips_nganggur:
            console.print(
                "[green]✨[/green] Semua IP Elastic udah nempel dengan baik!")
            console.print("Kagak ada yang perlu dibuang.")
            return

        # Bikin tabel dry run
        table = Table(title="🎯 EIP yang Bakal Dibuang",
                      show_header=True, header_style="bold yellow")
        table.add_column("Alamat IP", style="cyan")
        table.add_column("ID Alokasi", style="dim")
        table.add_column("Hemat Bulanan", style="green", justify="right")

        total_hemat = 0
        for eip in eips_nganggur:
            ip_publik = eip.get('PublicIp', 'Kagak Ada')
            allocation_id = eip.get('AllocationId', 'Kagak Ada')
            biaya_bulanan = 3.65
            total_hemat += biaya_bulanan

            table.add_row(
                ip_publik,
                allocation_id,
                f"${biaya_bulanan:.2f}"
            )

        console.print(table)

        # Panel ringkasan
        panel_ringkasan = Panel(
            f"[bold]Ringkasan[/bold]\n\n"
            f"EIP yang bakal dibuang: [bold yellow]{len(eips_nganggur)}[/bold yellow]\n"
            f"Hemat bulanan: [bold green]${total_hemat:.2f}[/bold green]\n"
            f"Hemat tahunan: [bold green]${total_hemat * 12:.2f}[/bold green]",
            title="💰 Potensi Penghematan",
            border_style="green"
        )
        console.print(panel_ringkasan)

    def ekspor_laporan(self, eips: List[Dict], nama_file: Optional[str] = None) -> None:
        """Ekspor laporan detail ke file JSON"""
        if not nama_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nama_file = f"laporan_eip_{timestamp}.json"

        data_laporan = {
            "timestamp": datetime.now().isoformat(),
            "region": self.region,
            "profile": self.profile,
            "statistik": self.statistik,
            "elastic_ips": []
        }

        for eip in eips:
            data_eip = {
                "ip_publik": eip.get('PublicIp'),
                "id_alokasi": eip.get('AllocationId'),
                "domain": eip.get('Domain'),
                "id_instance": eip.get('InstanceId'),
                "id_network_interface": eip.get('NetworkInterfaceId'),
                "udah_nempel": self._cek_eip_nempel(eip),
                "biaya_bulanan": 0.0 if self._cek_eip_nempel(eip) else 3.65
            }
            data_laporan["elastic_ips"].append(data_eip)

        try:
            with open(nama_file, 'w') as f:
                json.dump(data_laporan, f, indent=2)
            console.print(
                f"[green]✓[/green] Laporan udah diekspor ke: [bold]{nama_file}[/bold]")
        except Exception as e:
            console.print(f"[red]✗[/red] Gagal ekspor laporan: {e}")

    def tampilkan_statistik_akhir(self) -> None:
        """Tampilkan statistik eksekusi akhir"""
        if self.statistik['eips_dibuang'] > 0 or self.statistik['gagal_buang'] > 0:
            console.print("\n" + "="*60)
            console.print("[bold blue]📊 Ringkasan Eksekusi[/bold blue]")

            tabel_stats = Table(show_header=False, box=None)
            tabel_stats.add_column("Metrik", style="bold")
            tabel_stats.add_column("Nilai", justify="right")

            tabel_stats.add_row("Total EIP yang discan:",
                                f"[cyan]{self.statistik['total_eips']}[/cyan]")
            tabel_stats.add_row("EIP yang udah nempel:",
                                f"[green]{self.statistik['eips_nempel']}[/green]")
            tabel_stats.add_row(
                "EIP yang nganggur:", f"[yellow]{self.statistik['eips_nganggur']}[/yellow]")
            tabel_stats.add_row(
                "Berhasil dibuang:", f"[green]{self.statistik['eips_dibuang']}[/green]")

            if self.statistik['gagal_buang'] > 0:
                tabel_stats.add_row(
                    "Gagal buang:", f"[red]{self.statistik['gagal_buang']}[/red]")

            if self.statistik['eips_dibuang'] > 0:
                hemat_bulanan = self.statistik['eips_dibuang'] * 3.65
                tabel_stats.add_row(
                    "Hemat bulanan:", f"[bold green]${hemat_bulanan:.2f}[/bold green]")
                tabel_stats.add_row(
                    "Hemat tahunan:", f"[bold green]${hemat_bulanan * 12:.2f}[/bold green]")

            console.print(tabel_stats)
            console.print("="*60)


def bikin_parser() -> argparse.ArgumentParser:
    """Bikin dan konfigurasi argument parser"""
    parser = argparse.ArgumentParser(
        description="🌐 Tool Ngatur IP Elastic AWS Pake Bahasa Betawi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh penggunaan:
  %(prog)s --dry-run                    # Preview apa yang bakal dibuang
  %(prog)s --interactive                # Pilih-pilih EIP yang mau dibuang
  %(prog)s --batch --yes                # Buang semua EIP nganggur otomatis
  %(prog)s --profile prod --region us-west-2  # Pake profile dan region tertentu
  %(prog)s --export-report              # Bikin laporan JSON yang detail
        """
    )

    # Mode operasi
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='Mode preview - cuma liat apa yang bakal dibuang tanpa beneran buang'
    )
    mode_group.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Mode interaktif - konfirmasi manual tiap EIP yang mau dibuang'
    )
    mode_group.add_argument(
        '--batch', '-b',
        action='store_true',
        help='Mode batch - buang semua EIP nganggur sekaligus'
    )

    # Konfigurasi AWS
    parser.add_argument(
        '--profile', '-p',
        help='Profile AWS yang mau dipake (default: pake profile default)'
    )
    parser.add_argument(
        '--region', '-r',
        help='Region AWS (default: us-east-1 atau AWS_DEFAULT_REGION)'
    )

    # Opsi tambahan
    parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help='Skip konfirmasi (pake bareng --batch)'
    )
    parser.add_argument(
        '--export-report', '-e',
        action='store_true',
        help='Ekspor laporan detail ke file JSON'
    )
    parser.add_argument(
        '--report-file',
        help='Nama file custom buat laporan yang diekspor'
    )
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='Manager EIP AWS Edisi Betawi v2.0.0'
    )

    return parser


def main():
    """Main function aplikasi"""
    # Tampilkan banner
    console.print(Panel.fit(
        "[bold blue]🌐 Tool Ngatur IP Elastic AWS[/bold blue]\n",
        border_style="blue"
    ))

    # Parse argument
    parser = bikin_parser()
    args = parser.parse_args()

    # Default ke mode interaktif kalo kagak ada mode yang dipilih
    if not any([args.dry_run, args.interactive, args.batch]):
        args.interactive = True

    try:
        # Inisialisasi manager
        manager = ManagerElasticIPBetawi(
            profile=args.profile, region=args.region)

        # Ambil IP Elastic
        eips = manager.ambil_elastic_ips()

        # Tampilkan ringkasan
        manager.tampilkan_ringkasan_eip(eips)

        # Eksekusi berdasarkan mode
        if args.dry_run:
            manager.mode_dry_run(eips)
        elif args.interactive:
            manager.mode_interaktif(eips)
        elif args.batch:
            manager.mode_batch(eips, konfirmasi=not args.yes)

        # Ekspor laporan kalo diminta
        if args.export_report:
            manager.ekspor_laporan(eips, args.report_file)

        # Tampilkan statistik akhir
        manager.tampilkan_statistik_akhir()

        console.print(
            f"\n[green]✨[/green] Operasi selesai dengan sukses, Bos!")

    except KeyboardInterrupt:
        console.print(f"\n[yellow]⚠[/yellow] Operasi dibatalin sama user")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]✗[/red] Error yang kagak terduga: {e}")
        logging.exception("Error yang kagak terduga terjadi")
        sys.exit(1)


if __name__ == '__main__':
    main()
