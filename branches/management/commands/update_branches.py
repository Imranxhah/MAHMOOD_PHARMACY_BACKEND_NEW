from django.core.management.base import BaseCommand
from branches.models import Branch

class Command(BaseCommand):
    help = 'Seeds database with real Mahmood Pharmacy locations'

    def handle(self, *args, **kwargs):
        self.stdout.write('Deleting existing branches...')
        Branch.objects.all().delete()
        
        branches = [
            # 1. Airport Rd
            {
                "name": "Mahmood Pharmacy (Airport Rd)",
                "address": "Basement Ikram Center, Airport Rd, Khuda Buksh Colony Lahore, 54000",
                "phone": "03007757779",
                "latitude": 31.5434,
                "longitude": 74.3948,
                "timing": "24 Hours"
            },
            # 2. DHA Phase 2
            {
                "name": "Mahmood Pharmacy (DHA Phase 2)",
                "address": "FCM4+9XR, Sector Q DHA Phase 2, Lahore",
                "phone": "03208484742",
                "latitude": 31.4792,
                "longitude": 74.4086,
                "timing": "24 Hours"
            },
            # 3. DHA Phase 1 (Sec L)
            {
                "name": "Mahmood Pharmacy (DHA Phase 1 L Block)",
                "address": "H block, Commercial Market, near National Hospital, Sector L Dha Phase 1, Lahore, 54000",
                "phone": "03411100164",
                "latitude": 31.4815,
                "longitude": 74.3945,
                "timing": "24 Hours"
            },
            # 4. DHA Phase 4
            {
                "name": "Mahmood Pharmacy (DHA Phase 4)",
                "address": "F97M+2CG, Ground Floor, Plaza 63, Block DD, CCA, DHA Phase 4 Lahore",
                "phone": "03208484745",
                "latitude": 31.4688,
                "longitude": 74.4089,
                "timing": "24 Hours"
            },
            # 5. Cantt
            {
                "name": "Mahmood Pharmacy (Girja Chowk)",
                "address": "Girja Chowk, Cantt, Lahore, Punjab Cannt, Lahore, 58810",
                "phone": "03208661113",
                "latitude": 31.5222,
                "longitude": 74.3790,
                "timing": "24 Hours"
            },
            # 6. DHA Phase 5
            {
                "name": "Mahmood Pharmacy (DHA Phase 5)",
                "address": "5 Main Boulevard, Phase Sector C Dha, Lahore, 54792",
                "phone": "03000656656",
                "latitude": 31.4624,
                "longitude": 74.4497,
                "timing": "24 Hours"
            },
            # 7. Askari 11
            {
                "name": "Mahmood Pharmacy (Askari 11)",
                "address": "Ground & Mezzanine Floor, FC2M+Q86, Unit 4 Arain St 1, Sector B Askari 11 Sector B, Lahore",
                "phone": "03007757774",
                "latitude": 31.4469,
                "longitude": 74.4305,
                "timing": "8:00 AM - 12:00 PM"
            },
            # 8. Askari 10
            {
                "name": "Mahmood Pharmacy (Askari 10)",
                "address": "Block S, GCQC+RXH Commercial Market, Block A Askari X, Lahore",
                "phone": "03239488886",
                "latitude": 31.5432,
                "longitude": 74.3986,
                "timing": "24 Hours"
            },
            # 9. Gulberg III
            {
                "name": "Mahmood Pharmacy (Gulberg III)",
                "address": "Inside Al-Fatah, 51, Block B3 Block B 3 Gulberg III, Lahore",
                "phone": "03208484746",
                "latitude": 31.5054,
                "longitude": 74.3499,
                "timing": "9:00 AM - 10:00 PM"
            },
            # 10. Mustafabad
            {
                "name": "Mahmood Pharmacy (Mustafabad)",
                "address": "141 Allama Iqbal Rd, Mustafabad, Lahore",
                "phone": "03208661112",
                "latitude": 31.5604,
                "longitude": 74.3837,
                "timing": "24 Hours"
            },
            # 11. Johar Town
            {
                "name": "Mahmood Pharmacy (Johar Town)",
                "address": "Khayaban-e-Firdousi Road, near Shaukat Khanum Hospital, Block R3 Phase 2 Johar Town, Lahore, 54782",
                "phone": "03000657775",
                "latitude": 31.4633,
                "longitude": 74.2905,
                "timing": "24 Hours"
            },
            # 12. Allama Iqbal Town
            {
                "name": "Mahmood Pharmacy (Allama Iqbal Town)",
                "address": "477 Multan Rd, Zeenat Block Allama Iqbal Town, Lahore, 54000",
                "phone": "03411100165",
                "latitude": 31.5061,
                "longitude": 74.2862,
                "timing": "24 Hours"
            },
            # 13. Muslim Town
            {
                "name": "Mahmood Pharmacy (Wahdat Rd)",
                "address": "14 A Wahdat Rd, Muslim Town, Lahore, 54000",
                "phone": "03394100258",
                "latitude": 31.5244,
                "longitude": 74.3167,
                "timing": "24 Hours"
            },
            # 14. Faisal Town
            {
                "name": "Mahmood Pharmacy (Faisal Town)",
                "address": "Building No 26 D Faisal Town, Faisal, Town, Lahore, 54000",
                "phone": "03270544405",
                "latitude": 31.4883,
                "longitude": 74.3090,
                "timing": "24 Hours"
            },
            # 15. Daroghawala
            {
                "name": "Mahmood Pharmacy (Daroghawala)",
                "address": "Main Grand Trunk Rd, next to Gourmet Bakery, Daroghawala, Lahore, 54000",
                "phone": "03246334714",
                "latitude": 31.5879,
                "longitude": 74.4011,
                "timing": "24 Hours"
            },
            # 16. Wapda Town Phase 1
            {
                "name": "Mahmood Pharmacy (Wapda Town D3)",
                "address": "C7RF+7P 394, Block D3 Block D 3 Wapda Town Phase 1 Lahore",
                "phone": "03310404692",
                "latitude": 31.4283,
                "longitude": 74.2678,
                "timing": "24 Hours"
            },
            # 17. Samanabad
            {
                "name": "Mahmood Pharmacy (Samanabad)",
                "address": "13-A Poonch Rd, Samanabad Town, Lahore, 54000",
                "phone": "03003398899",
                "latitude": 31.5362,
                "longitude": 74.3005,
                "timing": "24 Hours"
            },
            # 18. PIA Society
            {
                "name": "Mahmood Pharmacy (PIA Society)",
                "address": "Plot 21 PIA Main Boulevard, Block E Pia Housing Scheme, Lahore, 54770",
                "phone": "03281607788",
                "latitude": 31.4398,
                "longitude": 74.2750,
                "timing": "24 Hours"
            },
            # 19. Wapda Town K2
            {
                "name": "Mahmood Pharmacy (Wapda Town K2)",
                "address": "Plot 331 Chasman Road, near Rehmat Chowk, Block K2 Block K 2 Wapda Town Phase 1 Lahore, 54770",
                "phone": "03211113605",
                "latitude": 31.4243,
                "longitude": 74.2655,
                "timing": "24 Hours"
            },
            # 20. Anarkali
            {
                "name": "Mahmood Pharmacy (Anarkali)",
                "address": "4 Baans Bazar, opposite Mayo Hospital Road, Anarkali Bazaar Gawalmandi, Lahore, 54000",
                "phone": "04237210986",
                "latitude": 31.5714,
                "longitude": 74.3134,
                "timing": "24 Hours"
            },
            # 21. Krishan Nagar
            {
                "name": "Mahmood Pharmacy (Krishan Nagar)",
                "address": "H79R+6QJ, Abdali Rd, Krishan Nagar Islampura, Lahore, 54000",
                "phone": "03002956669",
                "latitude": 31.5645,
                "longitude": 74.2954,
                "timing": "24 Hours"
            },
            # 22. Sanda
            {
                "name": "Mahmood Pharmacy (Sanda)",
                "address": "18 Sanda Rd, near Haq Orthopaedic Hospital, Sanda Islampura, Lahore, 54000",
                "phone": "03208484069",
                "latitude": 31.5487,
                "longitude": 74.2941,
                "timing": "24 Hours"
            },
            # 23. Bahria Town
            {
                "name": "Mahmood Pharmacy (Bahria Town)",
                "address": "52 B commercial, Sector C Bahria Town, Lahore",
                "phone": "03044707777",
                "latitude": 31.3821,
                "longitude": 74.1886,
                "timing": "24 Hours"
            },
            # 24. Thokar Niaz Baig
            {
                "name": "Mahmood Pharmacy (Thokar Niaz Baig)",
                "address": "2 KM, Thokar Niaz Baig, 53700 Multan Rd, Amarkot, Lahore",
                "phone": "03007757788",
                "latitude": 31.4711,
                "longitude": 74.2419,
                "timing": "24 Hours"
            },
            # 25. Ali Town
            {
                "name": "Mahmood Pharmacy (Ali Town)",
                "address": "4a Raiwind Rd, behind Faisal Bank, Ali Town Lahore",
                "phone": "03290633338",
                "latitude": 31.4616,
                "longitude": 74.2464,
                "timing": "24 Hours"
            },
            # 26. Etihad Town
            {
                "name": "Mahmood Pharmacy (Etihad Town)",
                "address": "mall in Lahore, Inside Al Fatah -Etihad Town, Raiwind Rd, Etihad Town, Lahore, 54000",
                "phone": "03091113616",
                "latitude": 31.4116,
                "longitude": 74.2255,
                "timing": "24 Hours"
            },
            # 27. Fazaia Housing
            {
                "name": "Mahmood Pharmacy (Fazaia)",
                "address": "Shop No. 1, Plot no. 2/A, Adda Plot, Main Round-About, Raiwind Rd, Block K Fazaia Housing Society, Lahore, 54000",
                "phone": "03411100163",
                "latitude": 31.4050,
                "longitude": 74.2200,
                "timing": "24 Hours"
            },
            # 28. Madina Tower
            {
                "name": "Mahmood Pharmacy (Madina Tower)",
                "address": "Ground Floor, Central Block, Plaza#1, Madina Tower, Lahore",
                "phone": "03001116737",
                "latitude": 31.4589,
                "longitude": 74.3013,
                "timing": "24 Hours"
            },
            # 29. Shahdara
            {
                "name": "Mahmood Pharmacy (Shahdara)",
                "address": "J7JP+2XW, Grand Trunk Rd, N 5 Shahdara Town, Lahore, 54950",
                "phone": "03224270810",
                "latitude": 31.6211,
                "longitude": 74.2824,
                "timing": "24 Hours"
            },
            # 30. Wocland (Defence Rd)
            {
                "name": "Mahmood Pharmacy (Defence Rd)",
                "address": "Wocland, Inside Al Fatah Store Defence Rd, Chowk, near Banu Hashim park, Wocland Villas, Lahore, 54000",
                "phone": "03211113610",
                "latitude": 31.4925,
                "longitude": 74.3311,
                "timing": "24 Hours"
            },
            # 31. Manawan
            {
                "name": "Mahmood Pharmacy (Manawan)",
                "address": "Sooter Mill, Main Grand Trunk Rd, near Manawan, Stop Tamhara Kot Pind, Lahore, 54000, Pakistan",
                "phone": "03315277519",
                "latitude": 31.5947,
                "longitude": 74.4447,
                "timing": "24 Hours"
            },
             # 32. DHA Phase 1 - 7H
            {
                "name": "Mahmood Pharmacy (DHA H-Block 1)",
                "address": "Shop No 7H Hblock Commerical Dha Phase 1 Lahore",
                "phone": "03208484741",
                "latitude": 31.4820,
                "longitude": 74.3950,
                "timing": "24 Hours"
            },
             # 33. DHA Phase 1 - 8H
            {
                "name": "Mahmood Pharmacy (DHA H-Block 2)",
                "address": "Shop No 8H Hblock Commerical Dha Phase 1 Lahore",
                "phone": "03007757773",
                "latitude": 31.4821,
                "longitude": 74.3951,
                "timing": "24 Hours"
            },
        ]

        count = 0
        for b_data in branches:
            Branch.objects.create(
                name=b_data["name"],
                address=b_data["address"],
                phone=b_data["phone"],
                latitude=b_data["latitude"],
                longitude=b_data["longitude"],
                timing=b_data["timing"],
                is_active=True
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {count} branches'))
