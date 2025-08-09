#!/usr/bin/env python3
"""
Tool Comprehensive Ngatur Unused AWS Resources Pake Bahasa Betawi
==============================================================

Tool super keren buat ngatur-ngatur berbagai unused AWS resources dengan fitur mantap:
- Support multiple resource types: EIP, ELB, EBS, Snapshots, RDS (Aurora), dan lainnya
- Mode interaktif dan batch dengan pemilihan resource yang flexible
- Tampilan console yang cakep pake warna-warni
- Error handling yang komprehensif dan logging yang oke
- Fitur dry-run buat nyoba-nyoba tanpa takut rusak
- Laporan detail dan cost analysis yang kece

Pembuat: Tim DevOps yang Kece
Versi: 3.0.0 Edisi Betawi Comprehensive
"""

import argparse
import boto3
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set

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
from rich.prompt import Confirm, Prompt, IntPrompt
from rich.logging import RichHandler
from rich.text import Text
from rich.tree import Tree

# Initialize colorama buat warna-warni cross-platform
colorama.init(autoreset=True)

# Initialize Rich console
console = Console()

class AWSResourceCleanerBetawi:
    """Kelas Manager AWS Resources yang Kece Pake Bahasa Betawi"""
    
    # Resource types yang didukung
    SUPPORTED_RESOURCES = {
        'eip': {
            'name': 'Elastic IP',
            'icon': '🌐',
            'cost_monthly': 3.65
        },
        'elb': {
            'name': 'Elastic Load Balancer',
            'icon': '⚖️',
            'cost_monthly': 22.50  # Classic ELB
        },
        'ebs': {
            'name': 'EBS Volumes',
            'icon': '💾',
            'cost_monthly': 10.0  # per 100GB gp3
        },
        'snapshot': {
            'name': 'EBS Snapshots',
            'icon': '📸',
            'cost_monthly': 5.0  # per 100GB
        },
        'rds': {
            'name': 'RDS Instances',
            'icon': '🗄️',
            'cost_monthly': 50.0  # minimal instance
        },
        'nat': {
            'name': 'NAT Gateways',
            'icon': '🚪',
            'cost_monthly': 32.85  # per NAT Gateway
        },
        'eni': {
            'name': 'Network Interfaces',
            'icon': '🔌',
            'cost_monthly': 1.0  # kalo detached
        }
    }
    
    def __init__(self, profile: Optional[str] = None, region: Optional[str] = None):
        """
        Inisialisasi Manager AWS Resources
        
        Args:
            profile: Profile AWS yang mau dipake
            region: Region AWS yang mau dioperasiin
        """
        self.profile = profile
        self.region = region or os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
        self.session = None
        self.clients = {}
        self.selected_resources = set()
        self.statistik = {
            'total_resources': 0,
            'unused_resources': 0,
            'deleted_resources': 0,
            'failed_deletions': 0,
            'total_savings': 0.0
        }
        
        self._setup_logging()
        self._inisialisasi_clients_aws()
    
    def _setup_logging(self) -> None:
        """Setup logging yang kece pake Rich handler"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(console=console, rich_tracebacks=True)]
        )
        self.logger = logging.getLogger("AWS_Resource_Cleaner_Betawi")
    
    def _inisialisasi_clients_aws(self) -> None:
        """Inisialisasi clients AWS dengan error handling yang mantap"""
        try:
            # Bikin session pake profile kalo ada
            if self.profile:
                self.session = boto3.Session(profile_name=self.profile)
                console.print(f"[green]✓[/green] Pake profile AWS: [bold cyan]{self.profile}[/bold cyan]")
            else:
                self.session = boto3.Session()
                console.print("[green]✓[/green] Pake kredensial AWS default nih")
            
            # Inisialisasi berbagai clients
            self.clients = {
                'ec2': self.session.client('ec2', region_name=self.region),
                'elbv2': self.session.client('elbv2', region_name=self.region),
                'elb': self.session.client('elb', region_name=self.region),
                'rds': self.session.client('rds', region_name=self.region)
            }
            
            # Test kredensial dengan panggil API sederhana
            self.clients['ec2'].describe_regions(RegionNames=[self.region])
            console.print(f"[green]✓[/green] Udah konek ke region AWS: [bold cyan]{self.region}[/bold cyan]")
            
        except ProfileNotFound as e:
            console.print(f"[red]✗[/red] Profile AWS '{self.profile}' kagak ketemu, Bos!")
            sys.exit(1)
        except (NoCredentialsError, PartialCredentialsError):
            console.print("[red]✗[/red] Kredensial AWS kagak ada atau kurang lengkap nih!")
            console.print("Tolong setting kredensial AWS pake:")
            console.print("  • aws configure")
            console.print("  • Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)")
            console.print("  • IAM roles (buat instance EC2)")
            sys.exit(1)
        except ClientError as e:
            console.print(f"[red]✗[/red] Error konek ke AWS: {e}")
            sys.exit(1)
    
    def tampilkan_menu_resource(self) -> None:
        """Tampilkan menu pemilihan resource types"""
        console.print("\n[bold blue]🎯 Pilih Resource Types yang Mau Dicek[/bold blue]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("No", justify="center", style="cyan", width=4)
        table.add_column("Icon", justify="center", width=6)
        table.add_column("Resource Type", style="green")
        table.add_column("Description", style="dim")
        table.add_column("Est. Cost/Month", style="yellow", justify="right")
        
        resource_list = list(self.SUPPORTED_RESOURCES.items())
        for i, (key, info) in enumerate(resource_list, 1):
            table.add_row(
                str(i),
                info['icon'],
                info['name'],
                f"{key.upper()} yang tidak terpakai",
                f"${info['cost_monthly']:.2f}"
            )
        
        table.add_row(
            "0",
            "🎯",
            "[bold]ALL RESOURCES[/bold]",
            "Pilih semua resource types",
            "[bold green]HEMAT MAX![/bold green]"
        )
        
        console.print(table)
    
    def pilih_resources(self) -> Set[str]:
        """Interactive resource selection"""
        self.tampilkan_menu_resource()
        
        while True:
            try:
                pilihan = Prompt.ask(
                    "\n[bold]Pilih resource yang mau dicek[/bold] (pisahin pake koma, contoh: 1,3,5 atau ketik 'all')",
                    default="all"
                ).lower().strip()
                
                if pilihan in ['all', '0', 'semua']:
                    return set(self.SUPPORTED_RESOURCES.keys())
                
                # Parse input
                selected_numbers = []
                for item in pilihan.split(','):
                    item = item.strip()
                    if item.isdigit():
                        selected_numbers.append(int(item))
                
                if not selected_numbers:
                    console.print("[red]Input kagak valid, coba lagi dong![/red]")
                    continue
                
                # Convert numbers to resource keys
                resource_keys = list(self.SUPPORTED_RESOURCES.keys())
                selected_resources = set()
                
                for num in selected_numbers:
                    if 1 <= num <= len(resource_keys):
                        selected_resources.add(resource_keys[num - 1])
                    else:
                        console.print(f"[red]Nomor {num} kagak valid![/red]")
                        continue
                
                if selected_resources:
                    # Tampilkan konfirmasi
                    console.print("\n[green]✓[/green] Resource yang dipilih:")
                    for resource in selected_resources:
                        info = self.SUPPORTED_RESOURCES[resource]
                        console.print(f"  {info['icon']} {info['name']}")
                    
                    if Confirm.ask("\nLanjut dengan pilihan ini?", default=True):
                        return selected_resources
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Operasi dibatalin oleh user[/yellow]")
                sys.exit(0)
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                continue
    
    def scan_elastic_ips(self) -> List[Dict]:
        """Scan unused Elastic IPs"""
        console.print("[cyan]🌐 Scanning Elastic IPs...[/cyan]")
        try:
            response = self.clients['ec2'].describe_addresses()
            eips = response.get('Addresses', [])
            
            unused_eips = []
            for eip in eips:
                if not (eip.get('InstanceId') or eip.get('NetworkInterfaceId')):
                    eip['resource_type'] = 'eip'
                    eip['estimated_cost'] = self.SUPPORTED_RESOURCES['eip']['cost_monthly']
                    unused_eips.append(eip)
            
            console.print(f"[green]✓[/green] Ketemu {len(unused_eips)} unused Elastic IPs")
            return unused_eips
            
        except ClientError as e:
            self.logger.error(f"Gagal scan EIPs: {e}")
            return []
    
    def scan_load_balancers(self) -> List[Dict]:
        """Scan unused Load Balancers"""
        console.print("[cyan]⚖️ Scanning Load Balancers...[/cyan]")
        unused_lbs = []
        
        try:
            # Scan ALB/NLB
            response = self.clients['elbv2'].describe_load_balancers()
            for lb in response.get('LoadBalancers', []):
                # Cek target groups
                targets_response = self.clients['elbv2'].describe_target_groups(
                    LoadBalancerArn=lb['LoadBalancerArn']
                )
                
                has_healthy_targets = False
                for tg in targets_response.get('TargetGroups', []):
                    health_response = self.clients['elbv2'].describe_target_health(
                        TargetGroupArn=tg['TargetGroupArn']
                    )
                    if any(target['TargetHealth']['State'] == 'healthy' 
                          for target in health_response.get('TargetHealthDescriptions', [])):
                        has_healthy_targets = True
                        break
                
                if not has_healthy_targets:
                    lb['resource_type'] = 'elb'
                    lb['estimated_cost'] = self.SUPPORTED_RESOURCES['elb']['cost_monthly']
                    unused_lbs.append(lb)
            
            # Scan Classic ELB
            response = self.clients['elb'].describe_load_balancers()
            for lb in response.get('LoadBalancerDescriptions', []):
                if not lb.get('Instances'):
                    lb['resource_type'] = 'elb'
                    lb['estimated_cost'] = self.SUPPORTED_RESOURCES['elb']['cost_monthly']
                    unused_lbs.append(lb)
            
            console.print(f"[green]✓[/green] Ketemu {len(unused_lbs)} unused Load Balancers")
            return unused_lbs
            
        except ClientError as e:
            self.logger.error(f"Gagal scan Load Balancers: {e}")
            return []
    
    def scan_ebs_volumes(self) -> List[Dict]:
        """Scan unused EBS Volumes"""
        console.print("[cyan]💾 Scanning EBS Volumes...[/cyan]")
        try:
            response = self.clients['ec2'].describe_volumes(
                Filters=[{'Name': 'state', 'Values': ['available']}]
            )
            
            unused_volumes = []
            for volume in response.get('Volumes', []):
                # Volume yang available = tidak attached
                volume['resource_type'] = 'ebs'
                # Hitung cost berdasarkan size (per GB)
                size_gb = volume.get('Size', 0)
                volume['estimated_cost'] = (size_gb / 100) * self.SUPPORTED_RESOURCES['ebs']['cost_monthly']
                unused_volumes.append(volume)
            
            console.print(f"[green]✓[/green] Ketemu {len(unused_volumes)} unused EBS Volumes")
            return unused_volumes
            
        except ClientError as e:
            self.logger.error(f"Gagal scan EBS Volumes: {e}")
            return []
    
    def scan_snapshots(self) -> List[Dict]:
        """Scan old/unused EBS Snapshots"""
        console.print("[cyan]📸 Scanning EBS Snapshots...[/cyan]")
        try:
            # Ambil snapshots yang owned by account ini
            response = self.clients['ec2'].describe_snapshots(OwnerIds=['self'])
            
            # Filter snapshots yang udah lama (> 30 hari) dan orphaned
            cutoff_date = datetime.now() - timedelta(days=30)
            unused_snapshots = []
            
            for snapshot in response.get('Snapshots', []):
                start_time = snapshot.get('StartTime')
                if start_time and start_time.replace(tzinfo=None) < cutoff_date:
                    # Cek apakah masih dipake buat AMI
                    ami_response = self.clients['ec2'].describe_images(
                        Filters=[
                            {'Name': 'block-device-mapping.snapshot-id', 'Values': [snapshot['SnapshotId']]}
                        ]
                    )
                    
                    if not ami_response.get('Images'):
                        snapshot['resource_type'] = 'snapshot'
                        # Hitung cost berdasarkan size
                        size_gb = snapshot.get('VolumeSize', 0)
                        snapshot['estimated_cost'] = (size_gb / 100) * self.SUPPORTED_RESOURCES['snapshot']['cost_monthly']
                        unused_snapshots.append(snapshot)
            
            console.print(f"[green]✓[/green] Ketemu {len(unused_snapshots)} old/unused Snapshots")
            return unused_snapshots
            
        except ClientError as e:
            self.logger.error(f"Gagal scan Snapshots: {e}")
            return []
    
    def scan_rds_instances(self) -> List[Dict]:
        """Scan unused/idle RDS instances"""
        console.print("[cyan]🗄️ Scanning RDS Instances...[/cyan]")
        try:
            response = self.clients['rds'].describe_db_instances()
            
            # Untuk demo, anggap RDS yang stopped sebagai unused
            unused_rds = []
            for db in response.get('DBInstances', []):
                if db.get('DBInstanceStatus') in ['stopped', 'available']:
                    # Bisa ditambah logic untuk cek connection metrics
                    db['resource_type'] = 'rds'
                    db['estimated_cost'] = self.SUPPORTED_RESOURCES['rds']['cost_monthly']
                    
                    # Cek kalo Aurora
                    if 'aurora' in db.get('Engine', '').lower():
                        db['estimated_cost'] *= 2  # Aurora lebih mahal
                    
                    unused_rds.append(db)
            
            console.print(f"[green]✓[/green] Ketemu {len(unused_rds)} potentially unused RDS instances")
            return unused_rds
            
        except ClientError as e:
            self.logger.error(f"Gagal scan RDS: {e}")
            return []
    
    def scan_nat_gateways(self) -> List[Dict]:
        """Scan unused NAT Gateways"""
        console.print("[cyan]🚪 Scanning NAT Gateways...[/cyan]")
        try:
            response = self.clients['ec2'].describe_nat_gateways()
            
            unused_nats = []
            for nat in response.get('NatGateways', []):
                if nat.get('State') == 'available':
                    # Cek route tables yang nge-reference NAT ini
                    routes_response = self.clients['ec2'].describe_route_tables(
                        Filters=[
                            {'Name': 'route.nat-gateway-id', 'Values': [nat['NatGatewayId']]}
                        ]
                    )
                    
                    # Kalo kagak ada route atau route table kagak dipake, consider unused
                    if not routes_response.get('RouteTables'):
                        nat['resource_type'] = 'nat'
                        nat['estimated_cost'] = self.SUPPORTED_RESOURCES['nat']['cost_monthly']
                        unused_nats.append(nat)
            
            console.print(f"[green]✓[/green] Ketemu {len(unused_nats)} potentially unused NAT Gateways")
            return unused_nats
            
        except ClientError as e:
            self.logger.error(f"Gagal scan NAT Gateways: {e}")
            return []
    
    def scan_network_interfaces(self) -> List[Dict]:
        """Scan unused Network Interfaces"""
        console.print("[cyan]🔌 Scanning Network Interfaces...[/cyan]")
        try:
            response = self.clients['ec2'].describe_network_interfaces(
                Filters=[{'Name': 'status', 'Values': ['available']}]
            )
            
            unused_enis = []
            for eni in response.get('NetworkInterfaces', []):
                # ENI yang available dan kagak attached ke instance apapun
                if not eni.get('Attachment'):
                    eni['resource_type'] = 'eni'
                    eni['estimated_cost'] = self.SUPPORTED_RESOURCES['eni']['cost_monthly']
                    unused_enis.append(eni)
            
            console.print(f"[green]✓[/green] Ketemu {len(unused_enis)} unused Network Interfaces")
            return unused_enis
            
        except ClientError as e:
            self.logger.error(f"Gagal scan Network Interfaces: {e}")
            return []
    
    def scan_resources(self, resource_types: Set[str]) -> List[Dict]:
        """Scan semua resource types yang dipilih"""
        console.print(f"\n[bold blue]🔍 Mulai scanning {len(resource_types)} resource types...[/bold blue]")
        
        all_resources = []
        scan_methods = {
            'eip': self.scan_elastic_ips,
            'elb': self.scan_load_balancers,
            'ebs': self.scan_ebs_volumes,
            'snapshot': self.scan_snapshots,
            'rds': self.scan_rds_instances,
            'nat': self.scan_nat_gateways,
            'eni': self.scan_network_interfaces
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            
            task = progress.add_task("Scanning resources...", total=len(resource_types))
            
            for resource_type in resource_types:
                if resource_type in scan_methods:
                    progress.update(task, description=f"Scanning {resource_type.upper()}...")
                    resources = scan_methods[resource_type]()
                    all_resources.extend(resources)
                    progress.advance(task)
                    time.sleep(0.5)  # Delay dikit biar kagak kena rate limiting
        
        return all_resources
    
    def tampilkan_hasil_scan(self, resources: List[Dict]) -> None:
        """Tampilkan hasil scan dengan tabel yang cakep"""
        if not resources:
            console.print("[green]✨[/green] Kagak ada unused resources yang ketemu! AWS account udah clean nih!")
            return
        
        # Group resources by type
        grouped_resources = {}
        total_cost = 0.0
        
        for resource in resources:
            resource_type = resource.get('resource_type', 'unknown')
            if resource_type not in grouped_resources:
                grouped_resources[resource_type] = []
            grouped_resources[resource_type].append(resource)
            total_cost += resource.get('estimated_cost', 0.0)
        
        # Bikin tree view
        tree = Tree("[bold blue]🗂️ Unused AWS Resources[/bold blue]")
        
        for resource_type, resource_list in grouped_resources.items():
            if resource_type in self.SUPPORTED_RESOURCES:
                info = self.SUPPORTED_RESOURCES[resource_type]
                type_cost = sum(r.get('estimated_cost', 0.0) for r in resource_list)
                
                type_node = tree.add(
                    f"{info['icon']} [bold]{info['name']}[/bold] "
                    f"([red]{len(resource_list)}[/red] items, "
                    f"[yellow]${type_cost:.2f}/month[/yellow])"
                )
                
                # Tambah detail items (max 5 buat readability)
                for i, resource in enumerate(resource_list[:5]):
                    detail = self._get_resource_detail(resource)
                    type_node.add(f"[dim]{detail}[/dim]")
                
                if len(resource_list) > 5:
                    type_node.add(f"[dim]... dan {len(resource_list) - 5} lainnya[/dim]")
        
        console.print(tree)
        
        # Panel ringkasan biaya
        panel_biaya = Panel(
            f"[bold]Summary[/bold]\n\n"
            f"Total unused resources: [bold red]{len(resources)}[/bold red]\n"
            f"Estimated monthly cost: [bold yellow]${total_cost:.2f}[/bold yellow]\n"
            f"Potential yearly savings: [bold green]${total_cost * 12:.2f}[/bold green]",
            title="💰 Cost Impact",
            border_style="red"
        )
        console.print(panel_biaya)
        
        # Update statistik
        self.statistik['total_resources'] = len(resources)
        self.statistik['unused_resources'] = len(resources)
        self.statistik['total_savings'] = total_cost
    
    def _get_resource_detail(self, resource: Dict) -> str:
        """Get detail string for a resource"""
        resource_type = resource.get('resource_type', 'unknown')
        
        if resource_type == 'eip':
            return f"IP: {resource.get('PublicIp', 'N/A')} (${resource.get('estimated_cost', 0):.2f}/month)"
        elif resource_type == 'elb':
            name = resource.get('LoadBalancerName') or resource.get('LoadBalancerArn', '').split('/')[-1]
            return f"LB: {name} (${resource.get('estimated_cost', 0):.2f}/month)"
        elif resource_type == 'ebs':
            return f"Volume: {resource.get('VolumeId', 'N/A')} ({resource.get('Size', 0)}GB, ${resource.get('estimated_cost', 0):.2f}/month)"
        elif resource_type == 'snapshot':
            return f"Snapshot: {resource.get('SnapshotId', 'N/A')} ({resource.get('VolumeSize', 0)}GB, ${resource.get('estimated_cost', 0):.2f}/month)"
        elif resource_type == 'rds':
            return f"RDS: {resource.get('DBInstanceIdentifier', 'N/A')} (${resource.get('estimated_cost', 0):.2f}/month)"
        elif resource_type == 'nat':
            return f"NAT: {resource.get('NatGatewayId', 'N/A')} (${resource.get('estimated_cost', 0):.2f}/month)"
        elif resource_type == 'eni':
            return f"ENI: {resource.get('NetworkInterfaceId', 'N/A')} (${resource.get('estimated_cost', 0):.2f}/month)"
        else:
            return f"Resource: {resource.get('id', 'N/A')}"
    
    def delete_resource(self, resource: Dict) -> bool:
        """Delete specific resource"""
        resource_type = resource.get('resource_type', 'unknown')
        
        try:
            if resource_type == 'eip':
                self.clients['ec2'].release_address(AllocationId=resource['AllocationId'])
                console.print(f"[green]✓[/green] Deleted EIP: {resource.get('PublicIp')}")
                
            elif resource_type == 'elb':
                if 'LoadBalancerArn' in resource:  # ALB/NLB
                    self.clients['elbv2'].delete_load_balancer(LoadBalancerArn=resource['LoadBalancerArn'])
                else:  # Classic ELB
                    self.clients['elb'].delete_load_balancer(LoadBalancerName=resource['LoadBalancerName'])
                console.print(f"[green]✓[/green] Deleted ELB: {resource.get('LoadBalancerName', 'ALB/NLB')}")
                
            elif resource_type == 'ebs':
                self.clients['ec2'].delete_volume(VolumeId=resource['VolumeId'])
                console.print(f"[green]✓[/green] Deleted EBS Volume: {resource.get('VolumeId')}")
                
            elif resource_type == 'snapshot':
                self.clients['ec2'].delete_snapshot(SnapshotId=resource['SnapshotId'])
                console.print(f"[green]✓[/green] Deleted Snapshot: {resource.get('SnapshotId')}")
                
            elif resource_type == 'rds':
                self.clients['rds'].delete_db_instance(
                    DBInstanceIdentifier=resource['DBInstanceIdentifier'],
                    SkipFinalSnapshot=True,
                    DeleteAutomatedBackups=True
                )
                console.print(f"[green]✓[/green] Deleted RDS: {resource.get('DBInstanceIdentifier')}")
                
            elif resource_type == 'nat':
                self.clients['ec2'].delete_nat_gateway(NatGatewayId=resource['NatGatewayId'])
                console.print(f"[green]✓[/green] Deleted NAT Gateway: {resource.get('NatGatewayId')}")
                
            elif resource_type == 'eni':
                self.clients['ec2'].delete_network_interface(NetworkInterfaceId=resource['NetworkInterfaceId'])
                console.print(f"[green]✓[/green] Deleted ENI: {resource.get('NetworkInterfaceId')}")
            
            self.statistik['deleted_resources'] += 1
            return True
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            console.print(f"[red]✗[/red] Failed to delete {resource_type}: {error_code}")
            self.logger.error(f"Failed to delete {resource_type}: {e}")
            self.statistik['failed_deletions'] += 1
            return False
    
    def mode_interaktif(self, resources: List[Dict]) -> None:
        """Mode interaktif buat delete resources satu-satu"""
        console.print("\n[bold blue]🎯 Mode Interaktif[/bold blue]")
        console.print("Review tiap unused resource terus pilih mau dihapus atau kagak.\n")
        
        if not resources:
            console.print("[green]✨[/green] Kagak ada unused resources!")
            return
        
        for i, resource in enumerate(resources, 1):
            detail = self._get_resource_detail(resource)
            resource_type = resource.get('resource_type', 'unknown')
            
            if resource_type in self.SUPPORTED_RESOURCES:
                info = self.SUPPORTED_RESOURCES[resource_type]
                console.print(f"\n[bold]Resource {i}/{len(resources)}:[/bold]")
                console.print(f"  {info['icon']} Type: [cyan]{info['name']}[/cyan]")
                console.print(f"  Detail: [dim]{detail}[/dim]")
                console.print(f"  Monthly Cost: [yellow]${resource.get('estimated_cost', 0):.2f}[/yellow]")
                
                if Confirm.ask(f"  Mau hapus resource ini, Bos?", default=False):
                    self.delete_resource(resource)
                else:
                    console.print(f"  [dim]Dilewatin aja...[/dim]")
    
    def mode_batch(self, resources: List[Dict], konfirmasi: bool = True) -> None:
        """Mode batch buat delete semua unused resources"""
        if not resources:
            console.print("[green]✨[/green] Kagak ada unused resources!")
            return
        
        console.print(f"\n[bold red]🔥 Mode Batch[/bold red]")
        console.print(f"Ketemu [bold]{len(resources)}[/bold] unused resources")
        
        if konfirmasi:
            total_savings = sum(r.get('estimated_cost', 0) for r in resources)
            if not Confirm.ask(
                f"Hapus SEMUA {len(resources)} unused resources? "
                f"(Ini bisa hemat ${total_savings:.2f}/month lho!)",
                default=False
            ):
                console.print("[yellow]⚠[/yellow] Operasi batch dibatalin")
                return
        
        # Delete resources pake progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            
            task = progress.add_task("Deleting resources...", total=len(resources))
            
            for resource in resources:
                resource_type = resource.get('resource_type', 'unknown')
                progress.update(task, description=f"Deleting {resource_type}...")
                self.delete_resource(resource)
                progress.advance(task)
                time.sleep(0.5)  # Delay dikit biar kagak kena rate limiting
    
    def mode_dry_run(self, resources: List[Dict]) -> None:
        """Mode dry run - cuma liat apa yang bakal dihapus"""
        console.print("\n[bold yellow]🧪 Mode Dry Run[/bold yellow]")
        console.print("Analisis apa yang bakal dihapus (kagak bakal ada perubahan beneran)\n")
        
        if not resources:
            console.print("[green]✨[/green] Kagak ada unused resources yang bakal dihapus!")
            return
        
        # Group by resource type
        grouped = {}
        total_savings = 0.0
        
        for resource in resources:
            resource_type = resource.get('resource_type', 'unknown')
            if resource_type not in grouped:
                grouped[resource_type] = []
            grouped[resource_type].append(resource)
            total_savings += resource.get('estimated_cost', 0.0)
        
        # Bikin tabel per resource type
        for resource_type, resource_list in grouped.items():
            if resource_type in self.SUPPORTED_RESOURCES:
                info = self.SUPPORTED_RESOURCES[resource_type]
                type_savings = sum(r.get('estimated_cost', 0.0) for r in resource_list)
                
                table = Table(
                    title=f"{info['icon']} {info['name']} yang Bakal Dihapus",
                    show_header=True,
                    header_style="bold yellow"
                )
                table.add_column("Resource ID", style="cyan")
                table.add_column("Detail", style="dim")
                table.add_column("Monthly Savings", style="green", justify="right")
                
                for resource in resource_list:
                    detail = self._get_resource_detail(resource)
                    table.add_row(
                        self._get_resource_id(resource),
                        detail,
                        f"${resource.get('estimated_cost', 0):.2f}"
                    )
                
                table.add_row(
                    "[bold]TOTAL[/bold]",
                    f"[bold]{len(resource_list)} items[/bold]",
                    f"[bold green]${type_savings:.2f}[/bold green]"
                )
                
                console.print(table)
                console.print()
        
        # Panel ringkasan total
        panel_ringkasan = Panel(
            f"[bold]Ringkasan Dry Run[/bold]\n\n"
            f"Total resources yang bakal dihapus: [bold yellow]{len(resources)}[/bold yellow]\n"
            f"Total penghematan bulanan: [bold green]${total_savings:.2f}[/bold green]\n"
            f"Total penghematan tahunan: [bold green]${total_savings * 12:.2f}[/bold green]",
            title="💰 Potensi Penghematan",
            border_style="green"
        )
        console.print(panel_ringkasan)
    
    def _get_resource_id(self, resource: Dict) -> str:
        """Get resource ID for display"""
        resource_type = resource.get('resource_type', 'unknown')
        
        if resource_type == 'eip':
            return resource.get('AllocationId', 'N/A')
        elif resource_type == 'elb':
            return resource.get('LoadBalancerName') or resource.get('LoadBalancerArn', '').split('/')[-1]
        elif resource_type == 'ebs':
            return resource.get('VolumeId', 'N/A')
        elif resource_type == 'snapshot':
            return resource.get('SnapshotId', 'N/A')
        elif resource_type == 'rds':
            return resource.get('DBInstanceIdentifier', 'N/A')
        elif resource_type == 'nat':
            return resource.get('NatGatewayId', 'N/A')
        elif resource_type == 'eni':
            return resource.get('NetworkInterfaceId', 'N/A')
        else:
            return 'N/A'
    
    def ekspor_laporan(self, resources: List[Dict], nama_file: Optional[str] = None) -> None:
        """Ekspor laporan detail ke file JSON"""
        if not nama_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nama_file = f"laporan_aws_cleanup_{timestamp}.json"
        
        # Group resources by type for report
        grouped_resources = {}
        for resource in resources:
            resource_type = resource.get('resource_type', 'unknown')
            if resource_type not in grouped_resources:
                grouped_resources[resource_type] = []
            grouped_resources[resource_type].append(resource)
        
        data_laporan = {
            "timestamp": datetime.now().isoformat(),
            "region": self.region,
            "profile": self.profile,
            "statistik": self.statistik,
            "resource_summary": {
                resource_type: {
                    "count": len(resource_list),
                    "total_cost": sum(r.get('estimated_cost', 0.0) for r in resource_list),
                    "resources": resource_list
                }
                for resource_type, resource_list in grouped_resources.items()
            },
            "total_potential_savings": {
                "monthly": sum(r.get('estimated_cost', 0.0) for r in resources),
                "yearly": sum(r.get('estimated_cost', 0.0) for r in resources) * 12
            }
        }
        
        try:
            with open(nama_file, 'w') as f:
                json.dump(data_laporan, f, indent=2, default=str)
            console.print(f"[green]✓[/green] Laporan udah diekspor ke: [bold]{nama_file}[/bold]")
        except Exception as e:
            console.print(f"[red]✗[/red] Gagal ekspor laporan: {e}")
    
    def tampilkan_statistik_akhir(self) -> None:
        """Tampilkan statistik eksekusi akhir"""
        if self.statistik['deleted_resources'] > 0 or self.statistik['failed_deletions'] > 0:
            console.print("\n" + "="*60)
            console.print("[bold blue]📊 Ringkasan Eksekusi[/bold blue]")
            
            tabel_stats = Table(show_header=False, box=None)
            tabel_stats.add_column("Metrik", style="bold")
            tabel_stats.add_column("Nilai", justify="right")
            
            tabel_stats.add_row("Total resources ditemukan:", f"[cyan]{self.statistik['total_resources']}[/cyan]")
            tabel_stats.add_row("Unused resources:", f"[yellow]{self.statistik['unused_resources']}[/yellow]")
            tabel_stats.add_row("Berhasil dihapus:", f"[green]{self.statistik['deleted_resources']}[/green]")
            
            if self.statistik['failed_deletions'] > 0:
                tabel_stats.add_row("Gagal hapus:", f"[red]{self.statistik['failed_deletions']}[/red]")
            
            if self.statistik['deleted_resources'] > 0:
                # Hitung actual savings berdasarkan yang berhasil dihapus
                # Kita assume rata-rata cost per resource
                avg_cost = self.statistik['total_savings'] / max(self.statistik['total_resources'], 1)
                actual_savings = self.statistik['deleted_resources'] * avg_cost
                
                tabel_stats.add_row("Penghematan bulanan:", f"[bold green]${actual_savings:.2f}[/bold green]")
                tabel_stats.add_row("Penghematan tahunan:", f"[bold green]${actual_savings * 12:.2f}[/bold green]")
            
            console.print(tabel_stats)
            console.print("="*60)


def bikin_parser() -> argparse.ArgumentParser:
    """Bikin dan konfigurasi argument parser"""
    parser = argparse.ArgumentParser(
        description="🚀 Tool Comprehensive Ngatur Unused AWS Resources Pake Bahasa Betawi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh penggunaan:
  %(prog)s --dry-run                    # Preview apa yang bakal dihapus
  %(prog)s --interactive                # Pilih-pilih resource yang mau dihapus
  %(prog)s --batch --yes                # Hapus semua unused resources otomatis
  %(prog)s --profile prod --region us-west-2  # Pake profile dan region tertentu
  %(prog)s --export-report              # Bikin laporan JSON yang detail
  %(prog)s --resources eip,ebs          # Cuma scan resource types tertentu
        """
    )
    
    # Mode operasi
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='Mode preview - cuma liat apa yang bakal dihapus tanpa beneran hapus'
    )
    mode_group.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Mode interaktif - konfirmasi manual tiap resource yang mau dihapus'
    )
    mode_group.add_argument(
        '--batch', '-b',
        action='store_true',
        help='Mode batch - hapus semua unused resources sekaligus'
    )
    
    # Resource selection
    parser.add_argument(
        '--resources', '-t',
        help='Resource types yang mau dicek (pisahin pake koma): eip,elb,ebs,snapshot,rds,nat,eni'
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
        version='AWS Resource Cleaner Edisi Betawi v3.0.0'
    )
    
    return parser


def main():
    """Main function aplikasi"""
    # Tampilkan banner
    console.print(Panel.fit(
        "[bold blue]🚀 AWS Resource Cleaner Comprehensive Edisi Betawi[/bold blue]\n"
        "[dim]Tool super keren buat bersihin unused AWS resources dengan hemat biaya maksimal![/dim]",
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
        manager = AWSResourceCleanerBetawi(profile=args.profile, region=args.region)
        
        # Pilih resource types
        if args.resources:
            # Parse dari command line
            selected_resources = set()
            for r in args.resources.split(','):
                r = r.strip().lower()
                if r in manager.SUPPORTED_RESOURCES:
                    selected_resources.add(r)
                else:
                    console.print(f"[yellow]Warning: Resource type '{r}' tidak didukung, dilewatin deh[/yellow]")
            
            if not selected_resources:
                console.print("[red]Kagak ada resource type yang valid![/red]")
                sys.exit(1)
        else:
            # Interactive selection
            selected_resources = manager.pilih_resources()
        
        console.print(f"\n[green]✓[/green] Akan scan resource types: {', '.join(selected_resources)}")
        
        # Scan resources
        unused_resources = manager.scan_resources(selected_resources)
        
        # Tampilkan hasil scan
        manager.tampilkan_hasil_scan(unused_resources)
        
        # Eksekusi berdasarkan mode
        if args.dry_run:
            manager.mode_dry_run(unused_resources)
        elif args.interactive:
            manager.mode_interaktif(unused_resources)
        elif args.batch:
            manager.mode_batch(unused_resources, konfirmasi=not args.yes)
        
        # Ekspor laporan kalo diminta
        if args.export_report:
            manager.ekspor_laporan(unused_resources, args.report_file)
        
        # Tampilkan statistik akhir
        manager.tampilkan_statistik_akhir()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ Operasi dibatalin oleh user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]✗ Error unexpected: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()