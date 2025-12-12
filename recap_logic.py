import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime
import numpy as np
from collections import defaultdict
import warnings
import io

# Force headless backend for PDF generation
import matplotlib
matplotlib.use('Agg')

warnings.filterwarnings('ignore')

# Set style
plt.style.use('ggplot') # Built-in matplotlib style similar to seaborn
plt.rcParams['font.family'] = 'sans-serif'

def parse_chat(text_content: str) -> dict:
    """
    Parses Groupchat text content into a structured dictionary.
    """
    data = text_content.splitlines()
    messages = []
    group_name = None
    
    for i, line in enumerate(data):
        line = line.strip()
        if not line:
            continue
            
        timestamp = None
        sender = None
        content = None
        
        try:
            if line.startswith('['):
                # Format: [DD.MM.YYYY HH:MM:SS] Sender: Content
                if '] ' in line:
                    timestamp, message = line.split('] ', 1)
                    timestamp = timestamp.strip('[')
                    if ': ' in message:
                        sender, content = message.split(': ', 1)
                    else:
                        content = message
                        sender = "System"
            elif ' - ' in line:
                # Format: DD.MM.YYYY Time - Sender: Content
                timestamp, message = line.split(' - ', 1)
                if ': ' in message:
                    sender, content = message.split(': ', 1)
                else:
                    content = message
                    sender = "System"
            
            if timestamp and sender and content:
                # Extract group name from the first line if it contains the encryption message
                if i == 0 and ("Messages and calls are end-to-end encrypted" in content or "uçtan uca şifrelidir" in content):
                    if sender != "System":
                        group_name = sender.strip()
                    # Do not continue, treat as message to ensure sender is captured if this is their only message
                    # continue
                
                messages.append([timestamp, sender, content])
        except ValueError:
            continue
    
    return {
        'messages': messages,
        'group_name': group_name,
        'columns': ['timestamp', 'sender', 'content']
    }


# Embedded Blacklist (from local karaliste.txt)
DEFAULT_BLACKLIST = {
    'oe', 'yarram', 'aminakodum', 'aminakodugum', 'sikik', 'yavşak', 'abaza', 'abazan', 'ag', 'ağzına sıçayım',
    'ahmak', 'allahsız', 'am', 'amarım', 'ambiti', 'am biti', 'amcığı', 'amcığın', 'amcığını', 'amcığınızı',
    'amcık', 'amcık hoşafı', 'amcıklama', 'amcıklandı', 'amcik', 'amck', 'amckl', 'amcklama', 'amcklaryla',
    'amckta', 'amcktan', 'amcuk', 'amık', 'amına', 'amınako', 'amına koy', 'amına koyarım', 'amına koyayım',
    'amınakoyim', 'amkoyim', 'amına koyyim', 'amına s', 'amına sikem', 'amına sokam', 'amın feryadı', 'amını', 'amını s',
    'amın oglu', 'amınoğlu', 'amın oğlu', 'amısına', 'amısını', 'amina', 'amina g', 'amina k', 'aminako',
    'aminakoyarim', 'amina koyarim', 'amina koyayım', 'amina koyayim', 'aminakoyim', 'aminda', 'amindan',
    'amindayken', 'amini', 'aminiyarraaniskiim', 'aminoglu', 'amin oglu', 'amiyum', 'amk', 'amkafa', 'amk çocuğu',
    'amlarnzn', 'amlı', 'amm', 'ammak', 'ammna', 'amn', 'amna', 'amnda', 'amndaki', 'amngtn', 'amnn', 'amona',
    'amq', 'amsız', 'amsiz', 'amsz', 'amteri', 'amugaa', 'amuğa', 'amuna', 'ana', 'anaaann', 'anal', 'analarn',
    'anam', 'anamla', 'anan', 'anana', 'anandan', 'anı', 'ananı', 'ananın', 'ananın am', 'ananın amı', 'ananın dölü',
    'ananınki', 'ananısikerim', 'ananı sikerim', 'ananısikeyim', 'ananı sikeyim', 'ananızın', 'ananızın am',
    'anani', 'ananin', 'ananisikerim', 'anani sikerim', 'ananisikeyim', 'anani sikeyim', 'anann', 'ananz', 'anas',
    'anasını', 'anasının am', 'anası orospu', 'anasi', 'anasinin', 'anay', 'anayin', 'angut', 'anneni', 'annenin',
    'annesiz', 'anuna', 'aptal', 'aq', 'a.q', 'a.q.', 'aq.', 'ass', 'atkafası', 'atmık', 'attırdığım', 'attrrm',
    'auzlu', 'avrat', 'ayklarmalrmsikerim', 'azdım', 'azdır', 'azdırıcı', 'babaannesi kaşar', 'babanı', 'babanın',
    'babani', 'babası pezevenk', 'bacağına sıçayım', 'bacına', 'bacını', 'bacının', 'bacini', 'bacn', 'bacndan',
    'bacy', 'bastard', 'basur', 'beyinsiz', 'bızır', 'bitch', 'biting', 'bok', 'boka', 'bokbok', 'bokça', 'bokhu',
    'bokkkumu', 'boklar', 'boktan', 'boku', 'bokubokuna', 'bokum', 'bombok', 'boner', 'bosalmak', 'boşalmak',
    'cenabet', 'cibiliyetsiz', 'cibilliyetini', 'cibilliyetsiz', 'cif', 'cikar', 'cim', 'çük', 'dalaksız', 'dallama',
    'daltassak', 'dalyarak', 'dalyarrak', 'dangalak', 'dassagi', 'diktim', 'dildo', 'dingil', 'dingilini', 'dinsiz',
    'dkerim', 'domal', 'domalan', 'domaldı', 'domaldın', 'domalık', 'domalıyor', 'domalmak', 'domalmış', 'domalsın',
    'domalt', 'domaltarak', 'domaltıp', 'domaltır', 'domaltırım', 'domaltip', 'domaltmak', 'dölü', 'dönek', 'düdük',
    'eben', 'ebeni', 'ebenin', 'ebeninki', 'ebleh', 'ecdadını', 'ecdadini', 'embesil', 'emi', 'fahise', 'fahişe',
    'feriştah', 'ferre', 'fuck', 'fucker', 'fuckin', 'fucking', 'gavad', 'gavat', 'geber', 'geberik', 'gebermek',
    'gebermiş', 'gebertir', 'gerızekalı', 'gerizekalı', 'gerizekali', 'gerzek', 'giberim', 'giberler', 'gibis',
    'gibiş', 'gibmek', 'gibtiler', 'goddamn', 'godoş', 'godumun', 'gotelek', 'gotlalesi', 'gotlu', 'gotten',
    'gotundeki', 'gotunden', 'gotune', 'gotunu', 'gotveren', 'goyiim', 'goyum', 'goyuyim', 'goyyim', 'göt',
    'göt deliği', 'götelek', 'göt herif', 'götlalesi', 'götlek', 'götoğlanı', 'göt oğlanı', 'götoş', 'götten',
    'götü', 'götün', 'götüne', 'götünekoyim', 'götüne koyim', 'götünü', 'götveren', 'göt veren', 'göt verir',
    'gtelek', 'gtn', 'gtnde', 'gtnden', 'gtne', 'gtten', 'gtveren', 'hasiktir', 'hassikome', 'hassiktir',
    'has siktir', 'hassittir', 'haysiyetsiz', 'hayvan herif', 'hoşafı', 'hödük', 'hsktr', 'huur', 'ıbnelık',
    'ibina', 'ibine', 'ibinenin', 'ibne', 'ibnedir', 'ibneleri', 'ibnelik', 'ibnelri', 'ibneni', 'ibnenin',
    'ibnerator', 'ibnesi', 'idiot', 'idiyot', 'imansz', 'ipne', 'iserim', 'işerim', 'itoğlu it', 'kafam girsin',
    'kafasız', 'kafasiz', 'kahpe', 'kahpenin', 'kahpenin feryadı', 'kaka', 'kaltak', 'kancık', 'kancik', 'kappe',
    'karhane', 'kaşar', 'kavat', 'kavatn', 'kaypak', 'kerane', 'kerhane', 'kerhanelerde', 'kevase', 'kevaşe',
    'kevvase', 'koca göt', 'koduğmun', 'koduğmunun', 'kodumun', 'kodumunun', 'koduumun', 'koyarm', 'koyayım',
    'koyiim', 'koyiiym', 'koyim', 'koyum', 'koyyim', 'krar', 'kukudaym', 'laciye boyadım', 'lavuk', 'liboş',
    'madafaka', 'mal', 'malafat', 'malak', 'manyak', 'mcik', 'meme', 'memelerini', 'mezveleli', 'minaamcık',
    'mincikliyim', 'mna', 'monakkoluyum', 'motherfucker', 'mudik', 'oc', 'ocuu', 'ocuun', 'OÇ', 'oç', 'o. çocuğu',
    'oğlan', 'oğlancı', 'oğlu it', 'orosbucocuu', 'orospu', 'orospucocugu', 'orospu cocugu', 'orospu çoc',
    'orospuçocuğu', 'orospu çocuğu', 'orospu çocuğudur', 'orospu çocukları', 'orospudur', 'orospular',
    'orospunun', 'orospunun evladı', 'orospuydu', 'orospuyuz', 'orostoban', 'orostopol', 'orrospu', 'oruspu',
    'oruspuçocuğu', 'oruspu çocuğu', 'osbir', 'ossurduum', 'ossurmak', 'ossuruk', 'osur', 'osurduu', 'osuruk',
    'osururum', 'otuzbir', 'öküz', 'öşex', 'patlak zar', 'penis', 'pezevek', 'pezeven', 'pezeveng', 'pezevengi',
    'pezevengin evladı', 'pezevenk', 'pezo', 'pic', 'pici', 'picler', 'piç', 'piçin oğlu', 'piç kurusu', 'piçler',
    'pipi', 'pipiş', 'pisliktir', 'porno', 'pussy', 'puşt', 'puşttur', 'rahminde', 'revizyonist', 's1kerim',
    's1kerm', 's1krm', 'sakso', 'saksofon', 'salaak', 'salak', 'saxo', 'sekis', 'serefsiz', 'sevgi koyarım',
    'sevişelim', 'sexs', 'sıçarım', 'sıçtığım', 'sıecem', 'sicarsin', 'sie', 'sik', 'sikdi', 'sikdiğim', 'sike',
    'sikecem', 'sikem', 'siken', 'sikenin', 'siker', 'sikerim', 'sikerler', 'sikersin', 'sikertir', 'sikertmek',
    'sikesen', 'sikesicenin', 'sikey', 'sikeydim', 'sikeyim', 'sikeym', 'siki', 'sikicem', 'sikici', 'sikien',
    'sikienler', 'sikiiim', 'sikiiimmm', 'sikiim', 'sikiir', 'sikiirken', 'sikik', 'sikil', 'sikildiini',
    'sikilesice', 'sikilmi', 'sikilmie', 'sikilmis', 'sikilmiş', 'sikilsin', 'sikim', 'sikimde', 'sikimden',
    'sikime', 'sikimi', 'sikimiin', 'sikimin', 'sikimle', 'sikimsonik', 'sikimtrak', 'sikin', 'sikinde',
    'sikinden', 'sikine', 'sikini', 'sikip', 'sikis', 'sikisek', 'sikisen', 'sikish', 'sikismis', 'sikiş',
    'sikişen', 'sikişme', 'sikitiin', 'sikiyim', 'sikiym', 'sikiyorum', 'sikkim', 'sikko', 'sikleri', 'sikleriii',
    'sikli', 'sikm', 'sikmek', 'sikmem', 'sikmiler', 'sikmisligim', 'siksem', 'sikseydin', 'sikseyidin', 'siksin',
    'siksinbaya', 'siksinler', 'siksiz', 'siksok', 'siksz', 'sikt', 'sikti', 'siktigimin', 'siktigiminin',
    'siktiğim', 'siktiğimin', 'siktiğiminin', 'siktii', 'siktiim', 'siktiimin', 'siktiiminin', 'siktiler',
    'siktim', 'siktim ', 'siktimin', 'siktiminin', 'siktir', 'siktir et', 'siktirgit', 'siktir git', 'siktirir',
    'siktiririm', 'siktiriyor', 'siktir lan', 'siktirolgit', 'siktir ol git', 'sittimin', 'sittir', 'skcem',
    'skecem', 'skem', 'sker', 'skerim', 'skerm', 'skeyim', 'skiim', 'skik', 'skim', 'skime', 'skmek', 'sksin',
    'sksn', 'sksz', 'sktiimin', 'sktrr', 'skyim', 'slaleni', 'sokam', 'sokarım', 'sokarim', 'sokarm',
    'sokarmkoduumun', 'sokayım', 'sokaym', 'sokiim', 'soktuğumunun', 'sokuk', 'sokum', 'sokuş', 'sokuyum',
    'soxum', 'sulaleni', 'sülaleni', 'sülalenizi', 'sürtük', 'şerefsiz', 'şıllık', 'taaklarn', 'taaklarna',
    'tarrakimin', 'tasak', 'tassak', 'taşak', 'taşşak', 'tipini s.k', 'tipinizi s.keyim', 'tiyniyat', 'toplarm',
    'topsun', 'totoş', 'vajina', 'vajinanı', 'veled', 'veledizina', 'veled i zina', 'verdiimin', 'weled',
    'weledizina', 'whore', 'xikeyim', 'yaaraaa', 'yalama', 'yalarım', 'yalarun', 'yaraaam', 'yarak', 'yaraksız',
    'yaraktr', 'yaram', 'yaraminbasi', 'yaramn', 'yararmorospunun', 'yarra', 'yarraaaa', 'yarraak', 'yarraam',
    'yarraamı', 'yarragi', 'yarragimi', 'yarragina', 'yarragindan', 'yarragm', 'yarrağ', 'yarrağım', 'yarrağımı',
    'yarraimin', 'yarrak', 'yarram', 'yarramin', 'yarraminbaşı', 'yarramn', 'yarran', 'yarrana', 'yarrrak',
    'yavak', 'yavş', 'yavşak', 'yavşaktır', 'yavuşak', 'yılışık', 'yilisik', 'yogurtlayam', 'yoğurtlayam',
    'yrrak', 'zıkkımım', 'zibidi', 'zigsin', 'zikeyim', 'zikiiim', 'zikiim', 'zikik', 'zikim', 'ziksiiin',
    'ziksiin', 'zulliyetini', 'zviyetini'
}

class RecapRenderer:
    def __init__(self, data: dict, user_map: dict = None, blacklist: set = None, max_users=15, is_dm=False):
        self.raw_messages = data.get('messages', [])
        self.columns = data.get('columns', ['timestamp', 'sender', 'content'])
        self.group_name = data.get('group_name')
        self.user_map = user_map
        self.max_users = max_users
        self.is_dm = is_dm
        self.chat_df = None
        # Use default blacklist if none provided
        self.blacklist_words = blacklist if blacklist else DEFAULT_BLACKLIST
        
        self._process_data()

    def _add_footer(self, fig):
        """Adds a branding footer to the figure."""
        # Add footer text with link
        fig.text(0.95, 0.03, 'lleonee.github.io/groupchat-recap/',
                ha='right', va='bottom', fontsize=12, fontweight='bold',
                color='#7f8c8d', url='https://lleonee.github.io/groupchat-recap/', alpha=0.8)

    def _process_data(self):
        self.chat_df = pd.DataFrame(self.raw_messages, columns=self.columns)
        
        # Remove system messages
        self.chat_df = self.chat_df[~self.chat_df['sender'].str.contains('grubu', case=False, na=False)]
        self.chat_df = self.chat_df[self.chat_df['sender'] != "System"]
        
        if self.group_name and not self.is_dm:
            self.chat_df = self.chat_df[self.chat_df['sender'] != self.group_name]
        
        # Handle User Mapping (Renaming)
        if self.user_map:
            self.chat_df['sender'] = self.chat_df['sender'].replace(self.user_map)

        # Escape special characters for Matplotlib (e.g. $) to prevent math rendering or errors
        # This fixes names looking like LaTeX equations
        self.chat_df['sender'] = self.chat_df['sender'].astype(str).apply(lambda x: x.replace('$', '\\$'))

        # Optimized Date Parsing
        # 1. Handle Turkish AM/PM using vectorized replace (faster than apply)
        self.chat_df['timestamp'] = self.chat_df['timestamp'].str.replace('öğleden sonra', 'PM', case=False)
        self.chat_df['timestamp'] = self.chat_df['timestamp'].str.replace('öğleden önce', 'AM', case=False)
        
        # 2. Detect format using Regex (More robust)
        import re
        detected_format = None
        
        if not self.chat_df.empty:
            # Check the first few samples to be sure
            sample = str(self.chat_df['timestamp'].iloc[0]).strip()
            
            # --- Regex Patterns ---
            
            # 1. Dots with Comma (DD.MM.YYYY, HH:MM:SS) - Most common TR
            if re.match(r'^\d{1,2}\.\d{1,2}\.\d{4},\s\d{1,2}:\d{2}:\d{2}$', sample):
                detected_format = '%d.%m.%Y, %H:%M:%S'
            
            # 2. Dots with space (DD.MM.YYYY HH:MM)
            elif re.match(r'^\d{1,2}\.\d{1,2}\.\d{4}\s\d{1,2}:\d{2}$', sample):
                detected_format = '%d.%m.%Y %H:%M'
            
            # 3. Dots with AM/PM (Turkish PM converted) -> DD.MM.YYYY PM HH:MM
            elif re.match(r'^\d{1,2}\.\d{1,2}\.\d{4}\s(AM|PM)\s\d{1,2}:\d{2}$', sample):
                detected_format = '%d.%m.%Y %p %I:%M'
                
            # 4. Slashes with Comma (MM/DD/YY, HH:MM:SS) - iOS US/UK
            elif re.match(r'^\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}$', sample):
                # Try DD/MM first
                detected_format = '%d/%m/%Y, %H:%M:%S'
                
            # 5. Slashes with AM/PM (MDY usually) -> MM/DD/YY, HH:MM PM
            elif re.search(r'\d{1,2}:\d{2}\s(AM|PM)', sample):
                if '/' in sample:
                    detected_format = '%m/%d/%Y, %I:%M %p' # US Standard
            
            # 6. Dash ISO-like (DD-MM-YYYY)
            elif re.match(r'^\d{1,2}-\d{1,2}-\d{4}\s\d{1,2}:\d{2}$', sample):
                detected_format = '%d-%m-%Y %H:%M'

        # Fallback: Trial and error if Regex missed it
        if not detected_format and not self.chat_df.empty:
            possible_formats = [
                '%d.%m.%Y, %H:%M:%S',
                '%d.%m.%Y %p %I:%M',
                '%d.%m.%Y %H:%M:%S',
                '%d.%m.%Y %H:%M'
            ]
            for idx in range(min(5, len(self.chat_df))):
                sample = self.chat_df['timestamp'].iloc[idx]
                for fmt in possible_formats:
                    try:
                        pd.to_datetime(sample, format=fmt)
                        detected_format = fmt
                        break
                    except (ValueError, TypeError):
                        continue
                if detected_format:
                    break
        
        if detected_format:
            self.chat_df['timestamp'] = pd.to_datetime(self.chat_df['timestamp'], format=detected_format, errors='coerce')
        else:
            self.chat_df['timestamp'] = pd.to_datetime(self.chat_df['timestamp'], errors='coerce')

        # Drop invalid dates
        self.chat_df = self.chat_df.dropna(subset=['timestamp'])
        
        # Filter by date range: 1 Aralık 2024 - 1 Aralık 2025 (Hardcoded as per original)
        start_date = pd.Timestamp('2024-12-01 00:00:00')
        end_date = pd.Timestamp('2025-12-01 00:00:00')
        self.chat_df = self.chat_df[
            (self.chat_df['timestamp'] >= start_date) & 
            (self.chat_df['timestamp'] < end_date)
        ]
        
        # Extract additional time features
        self.chat_df['date'] = self.chat_df['timestamp'].dt.date
        self.chat_df['hour'] = self.chat_df['timestamp'].dt.hour
        self.chat_df['year'] = self.chat_df['timestamp'].dt.year
        self.chat_df['month'] = self.chat_df['timestamp'].dt.month
        
        self.chat_df = self.chat_df.sort_values(by='timestamp')
        
        # Limit to top users
        if not self.chat_df.empty:
            total_senders_count = self.chat_df['sender'].nunique()
            if total_senders_count > self.max_users:
                 print(f"UYARI: Toplam {total_senders_count} kullanıcı var. Sadece en çok mesaj atan {self.max_users} kişi analiz edilecek.")
            
            top_users = self.chat_df['sender'].value_counts().head(self.max_users).index
            
            # If DM mode, strictly enforce 2 users effectively by taking top 2 if more exist
            if self.is_dm:
                if len(top_users) > 2:
                    top_users = self.chat_df['sender'].value_counts().head(2).index
            
            self.chat_df = self.chat_df[self.chat_df['sender'].isin(top_users)]
            
            # Calculate message features
            self.chat_df['message_length'] = self.chat_df['content'].str.len()
            
            # Identify conversation starts
            silence_threshold = pd.Timedelta(hours=1)
            self.chat_df['is_start'] = (self.chat_df['timestamp'] - self.chat_df['timestamp'].shift(1)) > silence_threshold
            self.chat_df['is_start'] = self.chat_df['is_start'].fillna(True)

    def get_slide_execution_list(self):
        """Returns a list of (slide_name, method) tuples for granular execution."""
        
        if self.is_dm:
            return [
                ("Title Slide", self.create_title_slide),
                
                # Volume & Time (Genel Bakış)
                ("Message Balance", self.create_dm_balance_slide),
                ("Activity Timeline", self.create_activity_timeline_slide), # Sohbet Ritmi
                ("Busiest Day", self.create_busiest_day_slide),
                ("Peak Hour", self.create_peak_hour_slide),
                ("Silent Hours", self.create_silent_hours_slide),
                ("Weekly Champion", self.create_weekly_champion_slide), # Added as requested
                
                # Behavioral (Davranışlar)
                ("Response Time", self.create_response_time_slide),
                ("First Message", self._create_first_message_wrapper), # Günaydın Sorumlusu
                ("Conversation Starter", self.create_simple_starter_slide),
                ("Wordiest Person", self.create_wordiest_person_slide),
                ("Caps Lock Champion", self.create_capslock_slide), # En Çok Bağıran (Added)
                
                # Content & Style (İçerik)
                ("Top Words", self.create_top_words_slide),
                ("Unique Words", self.create_unique_words_slide),
                ("Emoji & Punctuation", self.create_emoji_punctuation_slide),
                ("Profanity Usage", self.create_profanity_slide),
                ("Streaks", self.create_streak_slide),
                
                # Closing
                ("Methodology", self.create_calculation_explanation_slide),
                ("Closing Slide", self.create_closing_slide),
            ]
            
        return [
            ("Title Slide", self.create_title_slide),
            ("Most Active User", self.create_most_active_slide),
            ("Activity Timeline", self.create_activity_timeline_slide),
            ("First Message Winner", self._create_first_message_wrapper),
            ("First Responder", self._create_first_responder_wrapper),
            ("Night Owl", self.create_night_owl_slide),
            ("Morning Bird", self.create_morning_bird_slide),
            ("Peak Hour", self.create_peak_hour_slide),
            ("Conversation Starter", self.create_conversation_starter_slide),
            ("Conversation Continuation", self.create_conversation_continuation_slide),
            ("Wordiest Person", self.create_wordiest_person_slide),
            ("Emoji & Punctuation", self.create_emoji_punctuation_slide),
            ("Caps Lock Champion", self.create_capslock_slide),
            ("Pairwise Interaction", self.create_pairwise_slide),
            ("Mentions", self.create_mention_slide),
            ("Streaks", self.create_streak_slide),
            ("Top Words", self.create_top_words_slide),
            ("Unique Words", self.create_unique_words_slide),
            ("Weekly Champions", self.create_weekly_champions_slide),
            ("Weekly Timeline", self.create_weekly_timeline_slide),
            ("Profanity Usage", self.create_profanity_slide),
            ("Methodology", self.create_calculation_explanation_slide),
            ("Closing Slide", self.create_closing_slide),
        ]

    def create_capslock_slide(self, pdf):
        """Slide: Most Caps Lock Usage (Screaming)"""
        # Filter for messages that are all uppercase and longer than 3 characters (to avoid OK, TM etc)
        # Using vector operation
        
        # Check if content is string before checking isupper
        # Remove common punctuation to avoid "NASILSIN?" failing isupper check if punctuation is ignored or handled 
        # Standard isupper checks letters. "HELLO!" is upper. "HELLO" is upper.
        
        is_caps = (self.chat_df['content'].astype(str).str.len() > 3) & (self.chat_df['content'].astype(str).str.isupper())
        
        caps_counts = self.chat_df[is_caps]['sender'].value_counts()
        
        if caps_counts.empty:
            return
            
        winner = caps_counts.index[0]
        winner_count = caps_counts.iloc[0]
        
        fig = plt.figure(figsize=(16, 9))
        gs = fig.add_gridspec(2, 2, height_ratios=[1, 2], wspace=0.3)
        
        # Title
        ax_title = fig.add_subplot(gs[0, :])
        ax_title.axis('off')
        ax_title.text(0.5, 0.65, 'En Çok Bağıran',
                      ha='center', va='center', fontsize=46, fontweight='bold',
                      color='#C0392B')
        ax_title.text(0.5, 0.35, 'Caps Lock tuşunu bozan kişi!',
                      ha='center', va='center', fontsize=20,
                      color='#444444', style='italic')
        
        # Winner
        ax_winner = fig.add_subplot(gs[1, 0])
        ax_winner.axis('off')
        ax_winner.text(0.5, 0.65, winner,
                      ha='center', va='center', fontsize=52, fontweight='bold',
                      color='#E74C3C')
        ax_winner.text(0.5, 0.40, f'{winner_count} caps lock mesaj',
                      ha='center', va='center', fontsize=26,
                      color='#34495e')
        ax_winner.text(0.5, 0.20, 'NEDEN BAĞIRIYORSUN?',
                      ha='center', va='center', fontsize=16,
                      color='#555555', style='italic')
        
        # Chart
        ax_chart = fig.add_subplot(gs[1, 1])
        n_users = len(caps_counts)
        top_users = caps_counts.head(5) if n_users >= 7 else caps_counts
        colors = ['#E74C3C' if i == 0 else '#F1948A' for i in range(len(top_users))]
        ax_chart.barh(range(len(top_users)), top_users.values, color=colors, edgecolor='black')
        ax_chart.set_yticks(range(len(top_users)))
        ax_chart.set_yticklabels(top_users.index, fontsize=14)
        ax_chart.set_xlabel('Caps Lock Mesaj Sayısı', fontsize=14, fontweight='bold')
        ax_chart.grid(axis='x', linestyle='--', alpha=0.3)
        ax_chart.invert_yaxis()
        
        # Add labels
        for i, val in enumerate(top_users.values):
            ax_chart.text(val + max(top_users.values) * 0.02, i, f'{val}',
                         va='center', ha='left', fontsize=12, fontweight='bold', color='#34495e')
        
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        self._add_footer(fig)
        pdf.savefig(fig)
        plt.close()

        
    def _create_first_message_wrapper(self, pdf):
        """Wrapper to capture return value for first responder slide."""
        self.first_msg_winner = self.create_first_message_slide(pdf)
        
    def _create_first_responder_wrapper(self, pdf):
        """Wrapper to pass saved state."""
        self.create_first_responder_slide(pdf, getattr(self, 'first_msg_winner', None))

    def generate(self) -> bytes:
        """Generates the PDF and returns bytes (Synchronous legacy method)."""
        buffer = io.BytesIO()
        if self.chat_df is None or self.chat_df.empty:
             with PdfPages(buffer) as pdf:
                 fig, ax = plt.subplots(figsize=(16, 9))
                 ax.axis('off')
                 ax.text(0.5, 0.5, 'Analiz edilecek veri bulunamadı (2024-2025).', ha='center', va='center', fontsize=20)
                 self._add_footer(fig)
                 pdf.savefig(fig)
                 plt.close()
             return buffer.getvalue()

        # Run all slide creators
        with PdfPages(buffer) as pdf:
            for _, method in self.get_slide_execution_list():
                method(pdf)
            
            # Set metadata
            d = pdf.infodict()
            d['Title'] = 'Groupchat Yearly Recap'
            d['Author'] = 'PyScript Recap Generator'
            d['CreationDate'] = datetime.now()

        buffer.seek(0)
        return buffer.getvalue()

    # --- SLIDES ---

    def create_title_slide(self, pdf):
        fig, ax = plt.subplots(figsize=(16, 9))
        ax.axis('off')
        
        first_msg_date = self.chat_df['timestamp'].min()
        last_msg_date = self.chat_df['timestamp'].max()
        first_date_str = first_msg_date.strftime('%d.%m.%Y')
        last_date_str = last_msg_date.strftime('%d.%m.%Y')
        
        # Title Section
        if self.is_dm:
            # DM SPECIFIC TITLE
            users = self.chat_df['sender'].unique()
            title_name = " & ".join(users) if len(users) > 0 else "DM Sohbeti"
            
            ax.text(0.5, 0.80, title_name, ha='center', va='center', fontsize=42, fontweight='bold', color='#25D366')
            ax.text(0.5, 0.70, 'Yıllık DM Recap', ha='center', va='center', fontsize=42, fontweight='bold', color="#2C864D")
            year_y, date_y, stats_y, members_y_start = 0.60, 0.53, 0.43, -1.0 # Hide members list for DM (redundant)
            
        elif self.group_name:
            ax.text(0.5, 0.80, self.group_name, ha='center', va='center', fontsize=42, fontweight='bold', color='#25D366')
            ax.text(0.5, 0.70, 'Yıllık Groupchat Recap', ha='center', va='center', fontsize=42, fontweight='bold', color="#2C864D")
            year_y, date_y, stats_y, members_y_start = 0.60, 0.53, 0.43, 0.30
        else:
            ax.text(0.5, 0.75, 'Yıllık Groupchat Recap', ha='center', va='center', fontsize=42, fontweight='bold', color='#25D366')
            year_y, date_y, stats_y, members_y_start = 0.65, 0.58, 0.48, 0.35
        
        ax.text(0.5, year_y, '2024-2025', ha='center', va='center', fontsize=32, fontweight='bold', color='#075E54')
        ax.text(0.5, date_y, f"{first_date_str} - {last_date_str}", ha='center', va='center', fontsize=20, color='#075E54', style='italic')
        
        total_messages = len(self.chat_df)
        total_users = self.chat_df['sender'].nunique()
        days_diff = (last_msg_date - first_msg_date).days + 1
        daily_avg = total_messages / days_diff if days_diff > 0 else 0
        
        ax.text(0.5, stats_y, f"{total_messages:,} Mesaj - {total_users} Kişi - Günlük Ort: {daily_avg:.1f} mesaj", ha='center', va='center', fontsize=24, color='#34495e')
        
        if not self.is_dm:
            top_members = self.chat_df['sender'].value_counts().head(6).index.tolist()
            if len(top_members) > 3:
                ax.text(0.5, members_y_start, " • ".join(top_members[:3]), ha='center', va='center', fontsize=18, fontweight='bold', color='#2C3E50')
                ax.text(0.5, members_y_start - 0.05, " • ".join(top_members[3:]), ha='center', va='center', fontsize=18, fontweight='bold', color='#2C3E50')
            else:
                ax.text(0.5, members_y_start, " • ".join(top_members), ha='center', va='center', fontsize=18, fontweight='bold', color='#2C3E50')
        
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        self._add_footer(fig)
        pdf.savefig(fig)
        plt.close()

    def create_most_active_slide(self, pdf):
        """Slide: Most Active Person"""
        total_messages = self.chat_df['sender'].value_counts()
        winner = total_messages.index[0]
        winner_count = total_messages.iloc[0]
        
        fig = plt.figure(figsize=(16, 9))
        gs = fig.add_gridspec(2, 2, height_ratios=[1, 2], wspace=0.3)
        
        # Title
        ax_title = fig.add_subplot(gs[0, :])
        ax_title.axis('off')
        ax_title.text(0.5, 0.65, 'Grubun En Aktifi',
                      ha='center', va='center', fontsize=46, fontweight='bold',
                      color='#FFD700')
        ax_title.text(0.5, 0.35, 'Grupla sohbete doyamayan, en çok mesaj gönderen kişi.',
                      ha='center', va='center', fontsize=20,
                      color='#444444', style='italic')
        
        # Winner announcement
        ax_winner = fig.add_subplot(gs[1, 0])
        ax_winner.axis('off')
        ax_winner.text(0.5, 0.65, winner,
                      ha='center', va='center', fontsize=52, fontweight='bold',
                      color='#25D366')
        ax_winner.text(0.5, 0.40, f'{winner_count:,} mesaj',
                      ha='center', va='center', fontsize=34,
                      color='#34495e')
        ax_winner.text(0.5, 0.20, 'Onunla yarışamazsınız.',
                      ha='center', va='center', fontsize=16,
                      color='#555555', style='italic')
        
        # Bar chart
        ax_chart = fig.add_subplot(gs[1, 1])
        n_users = len(total_messages)
        top_users = total_messages.head(5) if n_users >= 7 else total_messages
        colors = ['#FFD700' if i == 0 else '#25D366' for i in range(len(top_users))]
        ax_chart.barh(range(len(top_users)), top_users.values, color=colors, edgecolor='black')
        ax_chart.set_yticks(range(len(top_users)))
        ax_chart.set_yticklabels(top_users.index, fontsize=14)
        ax_chart.set_xlabel('Mesaj Sayısı', fontsize=14, fontweight='bold')
        ax_chart.grid(axis='x', linestyle='--', alpha=0.3)
        ax_chart.invert_yaxis()
        
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        self._add_footer(fig)
        pdf.savefig(fig)
        plt.close()
        
    def create_night_owl_slide(self, pdf):
        """Slide: Night Owl (0-5 AM)"""
        night_messages = self.chat_df[
            (self.chat_df['hour'] >= 0) & (self.chat_df['hour'] < 5)
        ]
        
        # Calculate percentages
        total_counts = self.chat_df['sender'].value_counts()
        night_counts = night_messages['sender'].value_counts()
        
        # Reindex night_counts to include all users (fill with 0)
        night_counts = night_counts.reindex(total_counts.index, fill_value=0)
        
        # Calculate ratio
        night_ratios = (night_counts / total_counts * 100).fillna(0)
        night_ratios = night_ratios.sort_values(ascending=False)
        
        if len(night_ratios) == 0:
            return
        
        winner = night_ratios.index[0]
        winner_ratio = night_ratios.iloc[0]
        
        fig = plt.figure(figsize=(16, 9))
        gs = fig.add_gridspec(2, 2, height_ratios=[1, 2], wspace=0.3)
        
        # Title
        ax_title = fig.add_subplot(gs[0, :])
        ax_title.axis('off')
        ax_title.text(0.5, 0.65, 'Gece Kuşu',
                      ha='center', va='center', fontsize=46, fontweight='bold',
                      color='#4B0082')
        ax_title.text(0.5, 0.35, 'Uyku nedir bilmeyen kişi!',
                      ha='center', va='center', fontsize=20,
                      color='#444444', style='italic')
        
        # Winner
        ax_winner = fig.add_subplot(gs[1, 0])
        ax_winner.axis('off')
        ax_winner.text(0.5, 0.65, winner,
                      ha='center', va='center', fontsize=52, fontweight='bold',
                      color='#8B00FF')
        ax_winner.text(0.5, 0.40, f'%{winner_ratio:.1f} gece mesajı\n(00:00-05:00)',
                      ha='center', va='center', fontsize=26,
                      color='#34495e')
        ax_winner.text(0.5, 0.20, 'Mesajlarının çoğu gece yarısı!',
                      ha='center', va='center', fontsize=16,
                      color='#555555', style='italic')
        
        # Chart
        ax_chart = fig.add_subplot(gs[1, 1])
        n_users = len(night_ratios)
        top_users = night_ratios.head(5) if n_users >= 7 else night_ratios
        colors = ['#8B00FF' if i == 0 else '#FF6B9D' for i in range(len(top_users))]
        ax_chart.barh(range(len(top_users)), top_users.values, color=colors, edgecolor='black')
        ax_chart.set_yticks(range(len(top_users)))
        ax_chart.set_yticklabels(top_users.index, fontsize=14)
        ax_chart.set_xlabel('Gece Mesaj Oranı (%)', fontsize=14, fontweight='bold')
        ax_chart.grid(axis='x', linestyle='--', alpha=0.3)
        ax_chart.invert_yaxis()
        
        # Add percentage labels
        for i, v in enumerate(top_users.values):
            ax_chart.text(v + 0.5, i, f'%{v:.1f}', va='center', fontweight='bold')
        
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        self._add_footer(fig)
        pdf.savefig(fig)
        plt.close()
        
    def create_morning_bird_slide(self, pdf):
        """Slide: Morning Bird (05:00-09:30)"""
        # Filter messages between 05:00 and 09:30
        morning_messages = self.chat_df[
            ((self.chat_df['hour'] >= 5) & (self.chat_df['hour'] < 9)) | 
            ((self.chat_df['hour'] == 9) & (self.chat_df['timestamp'].dt.minute <= 30))
        ]
        
        # Calculate percentages
        total_counts = self.chat_df['sender'].value_counts()
        morning_counts = morning_messages['sender'].value_counts()
        
        # Reindex to include all users
        morning_counts = morning_counts.reindex(total_counts.index, fill_value=0)
        
        # Calculate ratio
        morning_ratios = (morning_counts / total_counts * 100).fillna(0)
        morning_ratios = morning_ratios.sort_values(ascending=False)
        
        if len(morning_ratios) == 0:
            return
        
        winner = morning_ratios.index[0]
        winner_ratio = morning_ratios.iloc[0]
        
        fig = plt.figure(figsize=(16, 9))
        gs = fig.add_gridspec(2, 2, height_ratios=[1, 2], wspace=0.3)
        
        # Title
        ax_title = fig.add_subplot(gs[0, :])
        ax_title.axis('off')
        ax_title.text(0.5, 0.65, 'Sabahçı',
                      ha='center', va='center', fontsize=46, fontweight='bold',
                      color='#FF8C00')  # Dark Orange
        ax_title.text(0.5, 0.35, 'Güne erken başlayan kişi!',
                      ha='center', va='center', fontsize=20,
                      color='#444444', style='italic')
        
        # Winner
        ax_winner = fig.add_subplot(gs[1, 0])
        ax_winner.axis('off')
        ax_winner.text(0.5, 0.65, winner,
                      ha='center', va='center', fontsize=52, fontweight='bold',
                      color='#FFA500') # Orange
        ax_winner.text(0.5, 0.40, f'%{winner_ratio:.1f} sabah mesajı\n(05:00-09:30)',
                      ha='center', va='center', fontsize=26,
                      color='#34495e')
        ax_winner.text(0.5, 0.20, 'Mesajlarının çoğu sabah saatlerinde.',
                      ha='center', va='center', fontsize=16,
                      color='#555555', style='italic')
        
        # Chart
        ax_chart = fig.add_subplot(gs[1, 1])
        n_users = len(morning_ratios)
        top_users = morning_ratios.head(5) if n_users >= 7 else morning_ratios
        colors = ['#FFA500' if i == 0 else '#FFD700' for i in range(len(top_users))] # Orange and Gold
        ax_chart.barh(range(len(top_users)), top_users.values, color=colors, edgecolor='black')
        ax_chart.set_yticks(range(len(top_users)))
        ax_chart.set_yticklabels(top_users.index, fontsize=14)
        ax_chart.set_xlabel('Sabah Mesaj Oranı (%)', fontsize=14, fontweight='bold')
        ax_chart.grid(axis='x', linestyle='--', alpha=0.3)
        ax_chart.invert_yaxis()
        
        # Add percentage labels
        for i, v in enumerate(top_users.values):
            ax_chart.text(v + 0.5, i, f'%{v:.1f}', va='center', fontweight='bold')
        
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        self._add_footer(fig)
        pdf.savefig(fig)
        plt.close()
        
    # --- NEW DM SLIDES ---
    
    def create_dm_balance_slide(self, pdf):
        """Slide: Message Balance (Text Volume Balance)"""
        counts = self.chat_df['sender'].value_counts()
        if len(counts) < 2:
            return
            
        u1, u2 = counts.index[0], counts.index[1]
        c1, c2 = counts.iloc[0], counts.iloc[1]
        total = c1 + c2
        p1 = (c1 / total) * 100
        p2 = (c2 / total) * 100
        
        fig = plt.figure(figsize=(16, 9))
        gs = fig.add_gridspec(2, 1, height_ratios=[1, 2])
        
        # Title
        ax_title = fig.add_subplot(gs[0])
        ax_title.axis('off')
        ax_title.text(0.5, 0.6, 'Mesaj Sayısı Dengesi', 
                      ha='center', va='center', fontsize=48, fontweight='bold', color='#e17055')
        
        sub_text = "Mükemmel uyum." if abs(p1-p2) < 10 else f"Sohbeti {u1} taşıyor!"
        ax_title.text(0.5, 0.3, sub_text, 
                      ha='center', va='center', fontsize=20, color='#636e72', style='italic')
        
        # Chart
        ax_chart = fig.add_subplot(gs[1])
        ax_chart.axis('off')
        
        # Simple stacked bar
        ax_chart.barh([0], [c1], color='#fab1a0', height=0.5, label=u1)
        ax_chart.barh([0], [c2], left=[c1], color='#74b9ff', height=0.5, label=u2)
        
        # Add text inside bars
        # User 1
        ax_chart.text(c1/2, 0, f"{u1}\n%{p1:.1f}\n({c1} mesaj)", ha='center', va='center', fontsize=30, fontweight='bold', color='white')
        
        # User 2
        ax_chart.text(c1 + c2/2, 0, f"{u2}\n%{p2:.1f}\n({c2} mesaj)", ha='center', va='center', fontsize=30, fontweight='bold', color='white')
        
        plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
        self._add_footer(fig)
        pdf.savefig(fig)
        plt.close()

    def create_response_time_slide(self, pdf):
        """Slide: Average Response Time"""
        df = self.chat_df.sort_values('timestamp').copy()
        
        # Calculate time diff from previous message
        df['time_diff'] = df['timestamp'].diff()
        
        # Identify sender switch
        df['prev_sender'] = df['sender'].shift(1)
        df['is_response'] = (df['sender'] != df['prev_sender']) & (df['prev_sender'].notna())
        
        # Filter only responses within 24 hours to exclude long gaps/sleep
        responses = df[df['is_response'] & (df['time_diff'] < pd.Timedelta(hours=24))]
        
        avg_times = responses.groupby('sender')['time_diff'].mean()
        
        if avg_times.empty:
            return
            
        fig = plt.figure(figsize=(16, 9))
        gs = fig.add_gridspec(2, 2, height_ratios=[1, 2], wspace=0.3)
        
        # Title
        ax_title = fig.add_subplot(gs[0, :])
        ax_title.axis('off')
        ax_title.text(0.5, 0.65, 'Mesaja Dönüş Hızı',
                      ha='center', va='center', fontsize=46, fontweight='bold', color='#0984e3')
        # Subtitle removed as requested
        
        # Determine format helper
        def format_delta(delta):
            minutes = delta.total_seconds() / 60
            if minutes < 60:
                return f"{int(minutes)} dk"
            else:
                hours = int(minutes / 60)
                mins = int(minutes % 60)
                return f"{hours}s {mins}dk"
        
        # Winner (Fastest)
        fastest_user = avg_times.idxmin()
        fastest_time = avg_times.min()
        
        ax_winner = fig.add_subplot(gs[1, 0])
        ax_winner.axis('off')
        ax_winner.text(0.5, 0.65, fastest_user,
                      ha='center', va='center', fontsize=52, fontweight='bold', color='#00b894')
        ax_winner.text(0.5, 0.40, f"Ort. {format_delta(fastest_time)}",
                      ha='center', va='center', fontsize=34, color='#2d3436')
        ax_winner.text(0.5, 0.20, 'Hızına yetişilemiyor!',
                      ha='center', va='center', fontsize=16, color='#636e72', style='italic')
        
        # Comparison Chart
        ax_chart = fig.add_subplot(gs[1, 1])
        users = avg_times.index
        times_min = avg_times.dt.total_seconds() / 60
        
        colors = ['#00b894' if u == fastest_user else '#fab1a0' for u in users]
        ax_chart.barh(users, times_min, color=colors, edgecolor='black')
        
        ax_chart.set_xlabel('Ortalama Cevap Süresi (Dakika)', fontsize=14, fontweight='bold')
        ax_chart.grid(axis='x', linestyle='--', alpha=0.3)
        
        # Add labels
        for i, (u, t) in enumerate(zip(users, times_min)):
            label = format_delta(pd.Timedelta(minutes=t))
            ax_chart.text(t + max(times_min)*0.02, i, label, va='center', fontweight='bold')
            
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        self._add_footer(fig)
        pdf.savefig(fig)
        plt.close()
        
    def create_simple_starter_slide(self, pdf):
        """Slide: Who started more conversations? (Simplified for DM)"""
        silence_threshold = pd.Timedelta(hours=1)
        df_sorted = self.chat_df.sort_values(by='timestamp').copy()
        
        # Identify start messages
        df_sorted['is_start'] = (df_sorted['timestamp'] - df_sorted['timestamp'].shift(1)) > silence_threshold
        df_sorted['is_start'] = df_sorted['is_start'].fillna(True)
        
        starter_counts = df_sorted[df_sorted['is_start']]['sender'].value_counts()
        if starter_counts.empty:
            return
            
        winner = starter_counts.index[0]
        count = starter_counts.iloc[0]
        
        fig = plt.figure(figsize=(16, 9))
        gs = fig.add_gridspec(2, 2, height_ratios=[1, 2])
        
        ax_title = fig.add_subplot(gs[0, :])
        ax_title.axis('off')
        ax_title.text(0.5, 0.65, 'Kim Daha Çok Konu Başlattı?',
                      ha='center', va='center', fontsize=46, fontweight='bold', color='#6c5ce7')
        ax_title.text(0.5, 0.35, 'Sessizliği bozan kahraman.',
                      ha='center', va='center', fontsize=20, color='#636e72', style='italic')
        
        # Winner
        ax_winner = fig.add_subplot(gs[1, 0])
        ax_winner.axis('off')
        ax_winner.text(0.5, 0.65, winner, ha='center', va='center', fontsize=52, fontweight='bold', color='#a29bfe')
        ax_winner.text(0.5, 0.40, f"{count} Konu", ha='center', va='center', fontsize=34, color='#2d3436')
        
        # Pie Chart
        ax_chart = fig.add_subplot(gs[1, 1])
        ax_chart.pie(starter_counts.values, labels=starter_counts.index, autopct='%1.1f%%', 
                     colors=['#a29bfe', '#dfe6e9', '#fab1a0'][:len(starter_counts)], textprops={'fontsize': 14})
        
        self._add_footer(fig)
        pdf.savefig(fig)
        plt.close()

    def create_busiest_day_slide(self, pdf):
        """Slide: Busiest Day (Most messages in one day)"""
        daily_counts = self.chat_df.groupby('date').size().sort_values(ascending=False)
        if daily_counts.empty:
            return
            
        busiest_date = daily_counts.index[0]
        msg_count = daily_counts.iloc[0]
        
        # Date formatting
        if isinstance(busiest_date, (datetime, pd.Timestamp)):
             date_str = busiest_date.strftime('%d.%m.%Y')
        else:
             date_str = str(busiest_date)
            
        fig, ax = plt.subplots(figsize=(16, 9))
        ax.axis('off')
        
        ax.text(0.5, 0.8, 'En Uzun Mesajlaşma Günü', ha='center', va='center', fontsize=46, fontweight='bold', color='#d63031')
        ax.text(0.5, 0.5, date_str, ha='center', va='center', fontsize=70, fontweight='bold', color='#2d3436')
        ax.text(0.5, 0.3, f"Tam {msg_count} mesaj!", ha='center', va='center', fontsize=30, color='#636e72')
        ax.text(0.5, 0.2, "Parmaklarınız ağrımadı mı?", ha='center', va='center', fontsize=20, style='italic', color='#b2bec3')
        
        self._add_footer(fig)
        pdf.savefig(fig)
        plt.close()

    def create_silent_hours_slide(self, pdf):
        """Slide: Silent Hours (Hours with least activity)"""
        hourly_counts = self.chat_df['hour'].value_counts().reindex(range(24), fill_value=0)
        
        # Find 3 consecutive hours with minimum sum
        min_sum = float('inf')
        start_hour = 0
        
        for i in range(24):
            # Handle wrapping (23, 0, 1)
            indices = [i, (i+1)%24, (i+2)%24]
            current_sum = sum(hourly_counts[idx] for idx in indices)
            if current_sum < min_sum:
                min_sum = current_sum
                start_hour = i
                
        end_hour = (start_hour + 3) % 24
        
        fig = plt.figure(figsize=(16, 9))
        gs = fig.add_gridspec(2, 2, height_ratios=[1, 2])
        
        ax_title = fig.add_subplot(gs[0, :])
        ax_title.axis('off')
        ax_title.text(0.5, 0.65, 'Sessizlik Haritası',
                      ha='center', va='center', fontsize=46, fontweight='bold', color='#2d3436')
        ax_title.text(0.5, 0.35, 'Muhtemelen uyuyorsunuz.',
                      ha='center', va='center', fontsize=20, color='#636e72', style='italic')
        
        # Info
        ax_info = fig.add_subplot(gs[1, 0])
        ax_info.axis('off')
        ax_info.text(0.5, 0.5, f"{start_hour:02d}:00 - {end_hour:02d}:00", 
                     ha='center', va='center', fontsize=60, fontweight='bold', color='#636e72')
        ax_info.text(0.5, 0.3, "En sessiz saatleriniz.", ha='center', va='center', fontsize=24, color='#b2bec3')
        
        # Chart (Clock style inverted)
        ax_chart = fig.add_subplot(gs[1, 1], projection='polar')
        theta = np.linspace(0, 2 * np.pi, 24, endpoint=False)
        radii = hourly_counts.values
        width = 2 * np.pi / 24
        
        # Highlight silence
        colors = ['#dfe6e9' if (h >= start_hour and h < start_hour+3) or (start_hour+3>=24 and (h>=start_hour or h<(start_hour+3)%24)) else '#636e72' for h in range(24)]
        
        ax_chart.bar(theta, radii, width=width, bottom=0, color=colors, alpha=0.7)
        ax_chart.set_theta_zero_location('N')
        ax_chart.set_theta_direction(-1)
        ax_chart.set_xticklabels([])
        ax_chart.set_yticklabels([])
        
        self._add_footer(fig)
        pdf.savefig(fig)
        plt.close()

    def create_first_message_slide(self, pdf):

        """Slide: First Message of the Day (after 06:00)"""
        # Filter messages after 06:00
        df_after_6am = self.chat_df[self.chat_df['timestamp'].dt.hour >= 6].copy()
        
        first_messages = df_after_6am.sort_values(by=['date', 'timestamp']).groupby('date').first()
        first_counts = first_messages['sender'].value_counts()
        
        if len(first_counts) == 0:
            return
        
        winner = first_counts.index[0]
        winner_count = first_counts.iloc[0]
        
        fig = plt.figure(figsize=(16, 9))
        gs = fig.add_gridspec(2, 2, height_ratios=[1, 2], wspace=0.3)
        
        # Title
        ax_title = fig.add_subplot(gs[0, :])
        ax_title.axis('off')
        
        title_text = 'Günün İlk Mesajını En Çok Atan Kişi' if getattr(self, 'is_dm', False) else 'Günün İlk Mesajı'
        
        ax_title.text(0.5, 0.65, title_text,
                      ha='center', va='center', fontsize=46, fontweight='bold',
                      color='#FFD700')
        # Subtitle removed as requested
        
        # Winner
        ax_winner = fig.add_subplot(gs[1, 0])
        ax_winner.axis('off')
        ax_winner.text(0.5, 0.65, winner,
                      ha='center', va='center', fontsize=52, fontweight='bold',
                      color='#FFA500')
        ax_winner.text(0.5, 0.40, f'{winner_count} gün\nİlk mesaj',
                      ha='center', va='center', fontsize=26,
                      color='#34495e')
        if not getattr(self, 'is_dm', False):
            ax_winner.text(0.5, 0.20, 'Gözünü açar açmaz grupta!',
                          ha='center', va='center', fontsize=16,
                          color='#555555', style='italic')
        
        # Chart
        ax_chart = fig.add_subplot(gs[1, 1])
        n_users = len(first_counts)
        top_users = first_counts.head(5) if n_users >= 7 else first_counts
        colors = ['#FFD700' if i == 0 else '#90EE90' for i in range(len(top_users))]
        ax_chart.barh(range(len(top_users)), top_users.values, color=colors, edgecolor='black')
        ax_chart.set_yticks(range(len(top_users)))
        ax_chart.set_yticklabels(top_users.index, fontsize=14)
        ax_chart.set_xlabel('İlk Mesajı Gönderdiği Gün Sayısı', fontsize=14, fontweight='bold')
        ax_chart.grid(axis='x', linestyle='--', alpha=0.3)
        ax_chart.invert_yaxis()
        
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        self._add_footer(fig)
        pdf.savefig(fig)
        plt.close()
        return winner
    
    def create_first_responder_slide(self, pdf, first_message_winner=None):
        """Slide: First Responder - Who responds to the day's first message"""
        from collections import defaultdict
        
        # Filter messages after 06:00
        df_after_6am = self.chat_df[self.chat_df['timestamp'].dt.hour >= 6].copy()
        
        # Group by date and sort by timestamp
        daily_messages = df_after_6am.sort_values('timestamp').groupby('date')
        
        first_responder_counts = defaultdict(int)
        
        for date, day_df in daily_messages:
            if len(day_df) < 2:
                continue
            
            # Find the first person to write
            first_sender = day_df.iloc[0]['sender']
            
            # Find the first different person to respond
            for idx in range(1, len(day_df)):
                responder = day_df.iloc[idx]['sender']
                if responder != first_sender:
                    first_responder_counts[responder] += 1
                    break
        
        if len(first_responder_counts) == 0:
            return
        
        # Sort by count
        sorted_responders = sorted(first_responder_counts.items(), key=lambda x: x[1], reverse=True)
        
        winner = sorted_responders[0][0]
        winner_count = sorted_responders[0][1]
        
        fig = plt.figure(figsize=(16, 9))
        gs = fig.add_gridspec(2, 2, height_ratios=[1, 2], wspace=0.3)
        
        # Title
        ax_title = fig.add_subplot(gs[0, :])
        ax_title.axis('off')
        ax_title.text(0.5, 0.65, 'Sabah İlk Cevap Veren',
                      ha='center', va='center', fontsize=46, fontweight='bold',
                      color='#27AE60')
        ax_title.text(0.5, 0.35, 'Günün ilk mesajına ilk cevap veren kişi! (saat 6\'dan sonra)',
                      ha='center', va='center', fontsize=20,
                      color='#444444', style='italic')
        
        # Winner
        ax_winner = fig.add_subplot(gs[1, 0])
        ax_winner.axis('off')
        ax_winner.text(0.5, 0.65, winner,
                      ha='center', va='center', fontsize=52, fontweight='bold',
                      color='#229954')
        ax_winner.text(0.5, 0.40, f'{winner_count} gün\nİlk cevap',
                      ha='center', va='center', fontsize=26,
                      color='#34495e')
        
        # Create dynamic text based on first message winner
        description_text = f"{first_message_winner}'ın günaydınına asla gecikmiyor!" if first_message_winner else 'Gruba hemen canlı veriyor!'
        ax_winner.text(0.5, 0.20, description_text,
                      ha='center', va='center', fontsize=16,
                      color='#555555', style='italic')
        
        # Chart
        ax_chart = fig.add_subplot(gs[1, 1])
        n_users = len(sorted_responders)
        top_users_data = sorted_responders[:5] if n_users >= 7 else sorted_responders
        names = [x[0] for x in top_users_data]
        counts = [x[1] for x in top_users_data]
        colors = ['#27AE60' if i == 0 else '#82E0AA' for i in range(len(names))]
        bars = ax_chart.barh(range(len(names)), counts, color=colors, edgecolor='black')
        ax_chart.set_yticks(range(len(names)))
        ax_chart.set_yticklabels(names, fontsize=14)
        ax_chart.set_xlabel('İlk Cevap Sayısı', fontsize=14, fontweight='bold')
        ax_chart.grid(axis='x', linestyle='--', alpha=0.3)
        ax_chart.invert_yaxis()
        
        # Add count labels
        for i, count in enumerate(counts):
            ax_chart.text(count + max(counts) * 0.02, i, f'{count}',
                         va='center', ha='left', fontsize=12, fontweight='bold', color='#34495e')
        
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        self._add_footer(fig)
        pdf.savefig(fig)
        plt.close()
        
    def create_peak_hour_slide(self, pdf):
        """Slide: Peak Activity Hour with Clock Chart"""
        # Calculate hourly message distribution
        hourly_counts = self.chat_df['hour'].value_counts().sort_index()
        peak_hour = hourly_counts.idxmax()
        peak_count = hourly_counts.max()
        
        fig = plt.figure(figsize=(16, 9))
        gs = fig.add_gridspec(2, 2, height_ratios=[1, 2])
        
        # Title
        ax_title = fig.add_subplot(gs[0, :])
        ax_title.axis('off')
        ax_title.text(0.5, 0.65, 'En Yoğun Saat',
                      ha='center', va='center', fontsize=46, fontweight='bold',
                      color='#E74C3C')
        # Subtitle removed
        
        # Winner
        ax_winner = fig.add_subplot(gs[1, 0])
        ax_winner.axis('off')
        ax_winner.text(0.5, 0.65, f'{peak_hour:02d}:00',
                      ha='center', va='center', fontsize=58, fontweight='bold',
                      color='#C0392B')
        ax_winner.text(0.5, 0.40, f'{peak_count} mesaj',
                      ha='center', va='center', fontsize=26,
                      color='#34495e')
        # Bottom subtitle removed
        
        # Clock chart
        ax_chart = fig.add_subplot(gs[1, 1], projection='polar')
        
        # Prepare data for polar plot
        theta = np.linspace(0, 2 * np.pi, 24, endpoint=False)
        radii = [hourly_counts.get(h, 0) for h in range(24)]
        width = 2 * np.pi / 24
        
        # Create bars
        colors_list = ['#E74C3C' if h == peak_hour else '#3498DB' for h in range(24)]
        bars = ax_chart.bar(theta, radii, width=width, bottom=0, color=colors_list, alpha=0.7, edgecolor='black')
        
        # Set labels
        ax_chart.set_theta_zero_location('N')
        ax_chart.set_theta_direction(-1)
        ax_chart.set_xticks(theta)
        ax_chart.set_xticklabels([f'{h:02d}' for h in range(24)], fontsize=10)
        ax_chart.set_ylim(0, max(radii) * 1.1)
        ax_chart.set_title('24 Saatlik Mesaj Dağılımı', pad=20, fontsize=14, fontweight='bold')
        
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        self._add_footer(fig)
        pdf.savefig(fig)
        plt.close()

    def create_conversation_starter_slide(self, pdf):
        """Slide: Conversation Starters vs First Responders"""
        # Define a threshold for silence (e.g., 1 hour)
        silence_threshold = pd.Timedelta(hours=1)
        
        # Sort by timestamp
        df_sorted = self.chat_df.sort_values(by='timestamp').copy()
        
        # Identify start messages (after 1 hour of silence)
        df_sorted['is_start'] = (df_sorted['timestamp'] - df_sorted['timestamp'].shift(1)) > silence_threshold
        df_sorted['is_start'] = df_sorted['is_start'].fillna(True)  # First message is always a start
        
        # Identify first responders (only if the responder is different from the starter)
        df_sorted['first_responder'] = (df_sorted['is_start'].shift(1).fillna(False)) & (df_sorted['sender'] != df_sorted['sender'].shift(1))
        
        # Count start messages and first responses per sender
        start_counts = df_sorted[df_sorted['is_start']].groupby('sender').size().sort_values(ascending=False)
        first_response_counts = df_sorted[df_sorted['first_responder']].groupby('sender').size().sort_values(ascending=False)
        
        if len(start_counts) == 0:
            return
        
        # Find the champions for both categories - AFTER sorting
        top_starter = start_counts.index[0]
        top_starter_count = start_counts.iloc[0]
        top_responder = first_response_counts.index[0] if len(first_response_counts) > 0 else None
        top_responder_count = first_response_counts.iloc[0] if len(first_response_counts) > 0 else 0
        
        # Get top 6 or all for each category
        n_starters = len(start_counts)
        n_responders = len(first_response_counts)
        top_starters = start_counts.head(6) if n_starters >= 7 else start_counts
        top_responders = first_response_counts.head(6) if n_responders >= 7 else first_response_counts
        
        fig = plt.figure(figsize=(16, 9))
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        gs = fig.add_gridspec(2, 2, height_ratios=[1, 2], wspace=0.4)
        
        # Title
        ax_title = fig.add_subplot(gs[0, :])
        ax_title.axis('off')
        ax_title.text(0.5, 0.65, 'Konuşma Başlatan vs İlk Cevap Veren',
                      ha='center', va='center', fontsize=46, fontweight='bold',
                      color='#E67E22')
        
        # Improved subtitle showing both stats
        if top_responder:
            subtitle = f'Konuşma Başlatan: {top_starter} ({top_starter_count}) | İlk Cevap Veren: {top_responder} ({top_responder_count})'
        else:
            subtitle = f'En çok: {top_starter} - {top_starter_count} konuşma başlattı'
        ax_title.text(0.5, 0.35, subtitle,
                      ha='center', va='center', fontsize=20,
                      color='#444444', style='italic')
        
        # Starters chart
        ax_starters = fig.add_subplot(gs[1, 0])
        
        # Shift right
        pos = ax_starters.get_position()
        ax_starters.set_position([pos.x0 + 0.06, pos.y0, pos.width - 0.06, pos.height])
        
        ax_starters.set_title('Konuşma Başlatan', fontsize=14, fontweight='bold', color='#D35400', pad=10)
        colors_start = ['#E67E22' if i == 0 else '#F39C12' for i in range(len(top_starters))]
        bars_start = ax_starters.barh(range(len(top_starters)), top_starters.values, 
                                      color=colors_start, edgecolor='black')
        ax_starters.set_yticks(range(len(top_starters)))
        ax_starters.set_yticklabels(top_starters.index, fontsize=12)
        ax_starters.set_xlabel('Konuşma Başlatan Sayısı', fontsize=12, fontweight='bold')
        ax_starters.grid(axis='x', linestyle='--', alpha=0.3)
        ax_starters.invert_yaxis()
        
        # Add count labels
        for i, val in enumerate(top_starters.values):
            ax_starters.text(val + max(top_starters.values) * 0.02, i, f'{val}',
                           va='center', ha='left', fontsize=12, fontweight='bold', color='#34495e')
        
        # First responders chart
        ax_responders = fig.add_subplot(gs[1, 1])
        
        # Shift right
        pos = ax_responders.get_position()
        ax_responders.set_position([pos.x0 + 0.06, pos.y0, pos.width - 0.06, pos.height])
        
        ax_responders.set_title('İlk Cevap Veren', fontsize=14, fontweight='bold', color='#2980B9', pad=10)
        if len(top_responders) > 0:
            colors_resp = ['#3498DB' if i == 0 else '#5DADE2' for i in range(len(top_responders))]
            bars_resp = ax_responders.barh(range(len(top_responders)), top_responders.values,
                                          color=colors_resp, edgecolor='black')
            ax_responders.set_yticks(range(len(top_responders)))
            ax_responders.set_yticklabels(top_responders.index, fontsize=12)
            ax_responders.set_xlabel('İlk Cevap Sayısı', fontsize=12, fontweight='bold')
            ax_responders.grid(axis='x', linestyle='--', alpha=0.3)
            ax_responders.invert_yaxis()
            
            # Add count labels
            for i, val in enumerate(top_responders.values):
                ax_responders.text(val + max(top_responders.values) * 0.02, i, f'{val}',
                               va='center', ha='left', fontsize=12, fontweight='bold', color='#34495e')
        
        self._add_footer(fig)
        pdf.savefig(fig)
        plt.close()
    
    def create_wordiest_person_slide(self, pdf):
        """Slide: Wordiest Person (Longest Average Messages)"""
        avg_length = self.chat_df.groupby('sender')['message_length'].mean().sort_values(ascending=False)
        
        if len(avg_length) == 0:
            return
        
        winner = avg_length.index[0]
        winner_length = avg_length.iloc[0]
        
        fig = plt.figure(figsize=(16, 9))
        gs = fig.add_gridspec(2, 2, height_ratios=[1, 2], wspace=0.3)
        
        # Title
        ax_title = fig.add_subplot(gs[0, :])
        ax_title.axis('off')
        ax_title.text(0.5, 0.65, 'En Uzun Mesajları Yazan',
                      ha='center', va='center', fontsize=46, fontweight='bold',
                      color='#FF6347')
        ax_title.text(0.5, 0.35, 'Kelimeler duygularına tercüman olamıyor!',
                      ha='center', va='center', fontsize=20,
                      color='#444444', style='italic')
        
        # Winner
        ax_winner = fig.add_subplot(gs[1, 0])
        ax_winner.axis('off')
        ax_winner.text(0.5, 0.65, winner,
                      ha='center', va='center', fontsize=52, fontweight='bold',
                      color='#DC143C')
        ax_winner.text(0.5, 0.40, f'{winner_length:.0f} karakter\nort. mesaj uzunlugu',
                      ha='center', va='center', fontsize=26,
                      color='#34495e')
        ax_winner.text(0.5, 0.20, 'Dostoyevski misin kardeşim?',
                      ha='center', va='center', fontsize=16,
                      color='#555555', style='italic')
        
        # Chart
        ax_chart = fig.add_subplot(gs[1, 1])
        n_users = len(avg_length)
        top_users = avg_length.head(5) if n_users >= 7 else avg_length
        colors = ['#FF6347' if i == 0 else '#FFB6C1' for i in range(len(top_users))]
        ax_chart.barh(range(len(top_users)), top_users.values, color=colors, edgecolor='black')
        ax_chart.set_yticks(range(len(top_users)))
        ax_chart.set_yticklabels(top_users.index, fontsize=14)
        ax_chart.set_xlabel('Ortalama Mesaj Uzunluğu (karakter)', fontsize=14, fontweight='bold')
        ax_chart.grid(axis='x', linestyle='--', alpha=0.3)
        ax_chart.invert_yaxis()
        
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        self._add_footer(fig)
        pdf.savefig(fig)
        plt.close()

    def create_top_words_slide(self, pdf):
        """Slide: Most Used Words (Global or Split for DM)"""
        
        # Helper to get top words from a dataframe
        def get_top_of_df(df_target):
            all_text = ' '.join(df_target['content'].astype(str))
            stop_words = {
                've', 'bir', 'bu', 'da', 'de', 'mi', 'mu', 'mü', 'için', 'ile', 'o', 'ne', 'var', 
                'ya', 'çok', 'ben', 'sen', 'biz', 'siz', 'onlar', 'daha', 'en', 'şey', 'gibi',
                'ama', 'veya', 'olan', 'oldu', 'yok', 'ki', 'mı', 'nasıl', 'neden', 'nerede',
                'kim', 'şimdi', 'sonra', 'var', 'yani', 'falan', 'işte', 'hani', 'böyle', 'öyle',
                'şu', 'bana', 'sana', 'ona', 'bunu', 'şunu', 'onu', 'the', 'a', 'an', 'and', 'or',
                'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do',
                'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'to',
                'message', 'deleted', 'omitted', 'media', 'image', 'video', 'audio', 'sticker',
                'null', 'undefined', 'edited', 'medya', 'dahil', 'edilmedi', 'mesaj', 'düzenlendi'
            }
            words_raw = all_text.lower().split()
            word_counts = defaultdict(int)
            for word in words_raw:
                clean_word = ''.join(c for c in word if c.isalnum() or c in 'çğıöşüÇĞİÖŞÜ')
                if len(clean_word) >= 3 and clean_word not in stop_words:
                    word_counts[clean_word] += 1
            return sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        # DM MODE: Split View
        if getattr(self, 'is_dm', False):
             users = self.chat_df['sender'].unique()
             if len(users) < 2:
                 return # Should not happen in valid DM
             
             u1, u2 = users[0], users[1]
             top_u1 = get_top_of_df(self.chat_df[self.chat_df['sender'] == u1])
             top_u2 = get_top_of_df(self.chat_df[self.chat_df['sender'] == u2])
             
             fig = plt.figure(figsize=(16, 9))
             gs = fig.add_gridspec(2, 2, height_ratios=[1, 4], wspace=0.3)
             
             # Title
             ax_title = fig.add_subplot(gs[0, :])
             ax_title.axis('off')
             ax_title.text(0.5, 0.65, 'EN ÇOK KULLANILAN KELİMELER',
                          ha='center', va='center', fontsize=46, fontweight='bold', color='#9B59B6')
             ax_title.text(0.5, 0.35, 'Her iki tarafın da dilinden düşürmediği kelimeler.',
                          ha='center', va='center', fontsize=20, color='#444444', style='italic')

             # User 1 Chart
             ax_u1 = fig.add_subplot(gs[1, 0])
             if top_u1:
                 w1 = [w[0] for w in top_u1]
                 c1 = [w[1] for w in top_u1]
                 ax_u1.barh(range(len(w1)), c1, color='#fab1a0', edgecolor='black')
                 ax_u1.set_yticks(range(len(w1)))
                 ax_u1.set_yticklabels(w1, fontsize=14, fontweight='bold')
                 ax_u1.set_title(u1, fontsize=24, fontweight='bold', color='#e17055')
                 ax_u1.invert_yaxis()
             else:
                 ax_u1.text(0.5, 0.5, "Yeterli veri yok", ha='center', va='center')
                 ax_u1.axis('off')

             # User 2 Chart
             ax_u2 = fig.add_subplot(gs[1, 1])
             if top_u2:
                 w2 = [w[0] for w in top_u2]
                 c2 = [w[1] for w in top_u2]
                 ax_u2.barh(range(len(w2)), c2, color='#74b9ff', edgecolor='black')
                 ax_u2.set_yticks(range(len(w2)))
                 ax_u2.set_yticklabels(w2, fontsize=14, fontweight='bold')
                 ax_u2.set_title(u2, fontsize=24, fontweight='bold', color='#0984e3')
                 ax_u2.invert_yaxis()
             else:
                 ax_u2.text(0.5, 0.5, "Yeterli veri yok", ha='center', va='center')
                 ax_u2.axis('off')
                 
             self._add_footer(fig)
             pdf.savefig(fig)
             plt.close()
             return

        # GROUP MODE: One Combined Chart (Existing Logic)
        top_words = get_top_of_df(self.chat_df)
        
        if len(top_words) == 0:
            return
        
        fig = plt.figure(figsize=(16, 9))
        gs = fig.add_gridspec(2, 1, height_ratios=[1, 3])
        
        # Title
        ax_title = fig.add_subplot(gs[0])
        ax_title.axis('off')
        ax_title.text(0.5, 0.65, 'EN ÇOK KULLANILAN KELİMELER',
                      ha='center', va='center', fontsize=46, fontweight='bold',
                      color='#9B59B6')
        
        sub_text = 'Ortak kelime dağarcığınız!' if getattr(self, 'is_dm', False) else 'Grubun favori kelimeleri!'
        ax_title.text(0.5, 0.35, sub_text,
                      ha='center', va='center', fontsize=20,
                      color='#444444', style='italic')
        
        # Word chart
        ax_chart = fig.add_subplot(gs[1])
        words_list = [w[0] for w in top_words]
        counts_list = [w[1] for w in top_words]
        
        # Create gradient colors
        colors = plt.cm.Purples(np.linspace(0.4, 0.9, len(words_list)))
        
        bars = ax_chart.barh(range(len(words_list)), counts_list, color=colors, edgecolor='black')
        ax_chart.set_yticks(range(len(words_list)))
        ax_chart.set_yticklabels(words_list, fontsize=16, fontweight='bold')
        ax_chart.set_xlabel('Kullanım Sayısı', fontsize=14, fontweight='bold')
        ax_chart.grid(axis='x', linestyle='--', alpha=0.3)
        ax_chart.invert_yaxis()
        
        # Add count labels on bars
        for i, (bar, count) in enumerate(zip(bars, counts_list)):
            ax_chart.text(count + max(counts_list) * 0.01, i, f'{count}',
                         va='center', fontsize=14, fontweight='bold')
        
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        self._add_footer(fig)
        pdf.savefig(fig)
        plt.close()
    
    def create_activity_timeline_slide(self, pdf):
        """Slide: Activity Timeline"""
        fig = plt.figure(figsize=(16, 9))
        gs = fig.add_gridspec(2, 1, height_ratios=[1, 3])
        
        # Title
        title_text = "Sohbet Ritmi" if getattr(self, "is_dm", False) else "Grup Aktivite Grafiği"
        
        ax_title = fig.add_subplot(gs[0])
        ax_title.axis('off')
        ax_title.text(0.5, 0.65, title_text,
                      ha='center', va='center', fontsize=46, fontweight='bold',
                      color='#2E86AB')
        ax_title.text(0.5, 0.35, 'Yıl boyunca mesajlaşma yoğunluğu',
                      ha='center', va='center', fontsize=20,
                      color='#444444', style='italic')
        
        # Timeline
        ax_timeline = fig.add_subplot(gs[1])
        messages_per_week = self.chat_df.set_index('timestamp').resample('W').size()
        
        ax_timeline.fill_between(messages_per_week.index, messages_per_week.values, 
                                alpha=0.3, color='#25D366')
        ax_timeline.plot(messages_per_week.index, messages_per_week.values,
                        color='#075E54', linewidth=2.5)
        ax_timeline.set_xlabel('Tarih', fontsize=14, fontweight='bold')
        ax_timeline.set_ylabel('Haftalık Mesaj Sayısı', fontsize=14, fontweight='bold')
        ax_timeline.grid(True, linestyle='--', alpha=0.3)
        ax_timeline.tick_params(labelsize=12)
        plt.setp(ax_timeline.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.15)
        self._add_footer(fig)
        pdf.savefig(fig)
        plt.close()
        
    def create_emoji_punctuation_slide(self, pdf):
        """Slide: Emoji and Punctuation Usage"""
        import re
        
        # Emoji pattern - covers most common emojis
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            u"\U0001F900-\U0001F9FF"  # supplemental symbols
            u"\U0001FA00-\U0001FAFF"  # extended symbols
            "]+", flags=re.UNICODE)
        
        # Punctuation marks to track
        punctuation_marks = ['!', '?', '...', ':)', ':(', ':D', 'xD', '<3']
        
        def count_emojis(text):
            return len(emoji_pattern.findall(str(text)))
        
        def count_punctuation(text):
            text_str = str(text)
            count = 0
            # Check for multi-character punctuation first
            for mark in ['...', ':)', ':(', ':D', 'xD', '<3']:
                count += text_str.count(mark)
            # Then single character
            count += text_str.count('!')
            count += text_str.count('?')
            return count
        
        # Calculate emoji and punctuation usage per sender
        emoji_counts = {}
        punct_counts = {}
        
        for sender in self.chat_df['sender'].unique():
            sender_msgs = self.chat_df[self.chat_df['sender'] == sender]['content']
            emoji_counts[sender] = sender_msgs.apply(count_emojis).sum()
            punct_counts[sender] = sender_msgs.apply(count_punctuation).sum()
        
        # Find winners
        emoji_winner = max(emoji_counts.items(), key=lambda x: x[1])
        punct_winner = max(punct_counts.items(), key=lambda x: x[1])
        
        # Get top users for charts
        top_emoji = sorted(emoji_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_punct = sorted(punct_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        fig = plt.figure(figsize=(16, 9))
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        gs = fig.add_gridspec(3, 2, height_ratios=[1, 1.2, 1.8], wspace=0.3)
        
        # Title
        ax_title = fig.add_subplot(gs[0, :])
        ax_title.axis('off')
        ax_title.text(0.5, 0.65, 'Emoji & Noktalama Kullanımı',
                      ha='center', va='center', fontsize=46, fontweight='bold',
                      color='#F39C12')
        ax_title.text(0.5, 0.35, 'Duygularınızı böyle ifade ediyorsunuz.',
                      ha='center', va='center', fontsize=20,
                      color='#444444', style='italic')
        
        # Emoji winner
        ax_emoji = fig.add_subplot(gs[1, 0])
        ax_emoji.axis('off')
        ax_emoji.text(0.5, 0.80, 'EMOJI KRALI/KRALICESI',
                      ha='center', va='center', fontsize=20, fontweight='bold',
                      color='#E67E22')
        ax_emoji.text(0.5, 0.50, emoji_winner[0],
                      ha='center', va='center', fontsize=36, fontweight='bold',
                      color='#D35400')
        ax_emoji.text(0.5, 0.25, f'{emoji_winner[1]} emoji',
                      ha='center', va='center', fontsize=22,
                      color='#34495e')
        
        # Punctuation winner
        ax_punct = fig.add_subplot(gs[1, 1])
        ax_punct.axis('off')
        ax_punct.text(0.5, 0.80, 'NOKTALAMA USTASI',
                      ha='center', va='center', fontsize=20, fontweight='bold',
                      color='#E67E22')
        ax_punct.text(0.5, 0.50, punct_winner[0],
                      ha='center', va='center', fontsize=36, fontweight='bold',
                      color='#D35400')
        ax_punct.text(0.5, 0.25, f'{punct_winner[1]} işaret',
                      ha='center', va='center', fontsize=22,
                      color='#34495e')

        # Emoji Chart
        ax_emoji_chart = fig.add_subplot(gs[2, 0])
        
        # Shift right
        pos = ax_emoji_chart.get_position()
        ax_emoji_chart.set_position([pos.x0 + 0.06, pos.y0, pos.width - 0.06, pos.height])
        
        names = [x[0] for x in top_emoji]
        counts = [x[1] for x in top_emoji]
        colors = ['#E67E22' if i == 0 else '#F5B041' for i in range(len(names))]
        bars = ax_emoji_chart.barh(range(len(names)), counts, color=colors, edgecolor='black')
        ax_emoji_chart.set_yticks(range(len(names)))
        ax_emoji_chart.set_yticklabels(names, fontsize=12)
        ax_emoji_chart.set_xlabel('Emoji Sayısı', fontsize=12, fontweight='bold')
        ax_emoji_chart.grid(axis='x', linestyle='--', alpha=0.3)
        ax_emoji_chart.invert_yaxis()
        
        # Add labels
        for i, v in enumerate(counts):
             ax_emoji_chart.text(v + max(counts)*0.02, i, str(v), va='center', fontweight='bold')

        # Punctuation Chart
        ax_punct_chart = fig.add_subplot(gs[2, 1])
        
        # Shift right
        pos = ax_punct_chart.get_position()
        ax_punct_chart.set_position([pos.x0 + 0.06, pos.y0, pos.width - 0.06, pos.height])
        
        names = [x[0] for x in top_punct]
        counts = [x[1] for x in top_punct]
        colors = ['#D35400' if i == 0 else '#DC7633' for i in range(len(names))]
        bars = ax_punct_chart.barh(range(len(names)), counts, color=colors, edgecolor='black')
        ax_punct_chart.set_yticks(range(len(names)))
        ax_punct_chart.set_yticklabels(names, fontsize=12)
        ax_punct_chart.set_xlabel('Noktalama Sayısı', fontsize=12, fontweight='bold')
        ax_punct_chart.grid(axis='x', linestyle='--', alpha=0.3)
        ax_punct_chart.invert_yaxis()
        
        # Add labels
        for i, v in enumerate(counts):
             ax_punct_chart.text(v + max(counts)*0.02, i, str(v), va='center', fontweight='bold')
        
        self._add_footer(fig)
        pdf.savefig(fig)
        plt.close()
    
    def create_pairwise_slide(self, pdf):
        """Slide: Pairwise Exchange Frequency"""
        from collections import defaultdict
        from datetime import timedelta
        
        # Count conversation sessions between pairs
        # A session = at least 5 messages between 2 people with no 3rd person interruption and no >30min gap
        pairwise_exchanges = defaultdict(int)
        
        # Optimize: Convert to numpy arrays/lists for faster iteration
        senders = self.chat_df['sender'].values
        timestamps = self.chat_df['timestamp'].values
        
        current_pair = None
        last_msg_time = None
        prev_sender = None
        session_message_count = 0
        
        # Define threshold
        thirty_min = np.timedelta64(30, 'm')
        
        for i in range(len(senders)):
            sender = senders[i]
            timestamp = timestamps[i]
            
            # Check if this continues the current session
            if current_pair:
                # Check if sender is one of the current pair
                if sender in current_pair:
                    # Check if gap is less than 30 minutes
                    if last_msg_time is not None and (timestamp - last_msg_time) <= thirty_min:
                        # Session continues
                        session_message_count += 1
                        last_msg_time = timestamp
                        prev_sender = sender
                        continue
                    else:
                        # Session ended due to time gap - count if >= 5 messages
                        if session_message_count >= 5:
                            pairwise_exchanges[current_pair] += 1
                        current_pair = None
                        session_message_count = 0
                else:
                    # Session ended due to 3rd person - count if >= 5 messages
                    if session_message_count >= 5:
                        pairwise_exchanges[current_pair] += 1
                    current_pair = None
                    session_message_count = 0
            
            # Try to start a new session
            if not current_pair and prev_sender and prev_sender != sender:
                # New session between these two people
                current_pair = tuple(sorted([prev_sender, sender]))
                session_message_count = 2  # Start with 2 (prev message + current)
                last_msg_time = timestamp
            
            prev_sender = sender
        
        # Don't forget to count the last session if it was valid
        if current_pair and session_message_count >= 5:
            pairwise_exchanges[current_pair] += 1
        
        # Find top pairs
        top_pairs = sorted(pairwise_exchanges.items(), key=lambda x: x[1], reverse=True)[:10]
        
        fig = plt.figure(figsize=(16, 9))
        gs = fig.add_gridspec(2, 2, height_ratios=[1, 2.5], wspace=0.3)
        
        # Title
        ax_title = fig.add_subplot(gs[0, :])
        ax_title.axis('off')
        ax_title.text(0.5, 0.65, 'En Çok Etkileşimde Olan İkililer',
                      ha='center', va='center', fontsize=46, fontweight='bold',
                      color='#16A085')
        ax_title.text(0.5, 0.35, 'Araya başka biri girmeden en az 5 mesaj süren konuşmalar',
                      ha='center', va='center', fontsize=20,
                      color='#444444', style='italic')
        
        # Top pair highlight - Vertical layout to prevent overlap
        if top_pairs:
            ax_top = fig.add_subplot(gs[1, 0])
            ax_top.axis('off')
            
            top_pair, top_count = top_pairs[0]
            
            # Title at the top
            ax_top.text(0.5, 0.90, 'EN BAĞLI İKİLİ',
                       ha='center', va='center', fontsize=20, fontweight='bold',
                       color='#117A65')
            
            # First person
            ax_top.text(0.5, 0.70, top_pair[0],
                       ha='center', va='center', fontsize=28, fontweight='bold',
                       color='#16A085', wrap=True)
            
            # Arrow
            ax_top.text(0.5, 0.52, '↕',
                       ha='center', va='center', fontsize=32,
                       color='#444444')
            
            # Second person
            ax_top.text(0.5, 0.35, top_pair[1],
                       ha='center', va='center', fontsize=28, fontweight='bold',
                       color='#16A085', wrap=True)
            
            # Count at the bottom
            ax_top.text(0.5, 0.15, f'{top_count} konuşma oturumu',
                       ha='center', va='center', fontsize=22,
                       color='#34495e')
        
        # Top 10 pairs chart - reduced to 6 for better readability
        ax_chart = fig.add_subplot(gs[1, 1])
        ax_chart.set_title('Top İkililer', fontsize=14, fontweight='bold', color='#117A65', pad=10)
        if top_pairs:
            # Limit to 6 pairs for better spacing
            display_pairs = top_pairs[:6]
            pair_labels = [f"{pair[0]} ↔ {pair[1]}" for pair, _ in display_pairs]
            counts = [count for _, count in display_pairs]
            
            colors = ['#16A085' if i == 0 else '#48C9B0' for i in range(len(pair_labels))]
            bars = ax_chart.barh(range(len(pair_labels)), counts, color=colors, edgecolor='black')
            ax_chart.set_yticks(range(len(pair_labels)))
            ax_chart.set_yticklabels(pair_labels, fontsize=11)
            ax_chart.set_xlabel('Konuşma Oturumu Sayısı', fontsize=12, fontweight='bold')
            ax_chart.grid(axis='x', linestyle='--', alpha=0.3)
            ax_chart.invert_yaxis()
            
            # Add count labels
            for i, (bar, count) in enumerate(zip(bars, counts)):
                ax_chart.text(count + max(counts) * 0.02, i, f'{count}',
                            va='center', ha='left', fontsize=11, fontweight='bold', color='#34495e')
        
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        self._add_footer(fig)
        pdf.savefig(fig)
        plt.close()
    
    def create_mention_slide(self, pdf):
        """Slide: Mention/İğneleme Analysis"""
        from collections import defaultdict
        
        # Get all user names
        users = self.chat_df['sender'].unique()
        
        # Count mentions: who mentions whom
        mention_matrix = defaultdict(lambda: defaultdict(int))
        total_mentions_received = defaultdict(int)
        total_mentions_given = defaultdict(int)
        
        # Optimize: Iterate over users instead of messages (O(Users * Messages) but vectorized)
        all_content = self.chat_df['content'].astype(str).str.lower()
        
        for user in users:
            user_lower = user.lower()
            
            # Prepare search patterns (name parts >= 3 chars)
            name_parts = [p for p in user_lower.split() if len(p) >= 3]
            if not name_parts:
                name_parts = [user_lower]
            
            import re
            escaped_parts = []
            for p in name_parts:
                esc = re.escape(p)
                if len(esc) > 0:
                    # Logic: 
                    # 1. Base name (escaped)
                    # 2. Allow last char to repeat (e.g. "cannn") -> convert last char "n" to "n*"
                    # 3. Allow up to 2 extra chars at the end (e.g. "cano", "canım") -> ".{0,2}"
                    # 4. Must end there (word boundary) -> "\b"
                    
                    # Separate last char for repetition
                    base = esc[:-1]
                    last = esc[-1]
                    
                    # Pattern: Start word boundary + base + last_char(repeated) + 0-2 any chars + End word boundary
                    # Note: We use \b at start to avoid matching inside other words (e.g. "Bacan" for "Can")
                    part_pattern = fr"\b{base}{last}+.{{0,2}}\b"
                    escaped_parts.append(part_pattern)
            
            pattern = '|'.join(escaped_parts)
            
            # Vectorized search: Find all messages containing any name part
            # Use count since a name might appear multiple times in one message? 
            # Original logic was "is_mentioned" boolean per message. Let's stick to boolean to match logic.
            # contains is faster than counting regex matches
            
            has_mention = all_content.str.contains(pattern, case=False, regex=True, na=False)
            
            # Filter messages that have mentions
            # We also need to exclude self-mentions, so we filter by sender != user
            mentions_df = self.chat_df[has_mention & (self.chat_df['sender'] != user)]
            
            if not mentions_df.empty:
                # Group by sender to see who mentioned this user
                mention_counts = mentions_df['sender'].value_counts()
                
                total_mentions_received[user] = mention_counts.sum()
                
                for sender, count in mention_counts.items():
                    mention_matrix[sender][user] = count
                    total_mentions_given[sender] += count
        
        # Find statistics
        # 1. Most mentioned person
        most_mentioned = max(total_mentions_received.items(), key=lambda x: x[1]) if total_mentions_received else (None, 0)
        
        # 2. Person who mentions others the most
        most_mentioner = max(total_mentions_given.items(), key=lambda x: x[1]) if total_mentions_given else (None, 0)
        
        # 3. Strongest mention relationship (A -> B)
        strongest_link = (None, None, 0)
        for mentioner in mention_matrix:
            for mentioned, count in mention_matrix[mentioner].items():
                if count > strongest_link[2]:
                    strongest_link = (mentioner, mentioned, count)
        
        fig = plt.figure(figsize=(16, 9))
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, wspace=0.35, hspace=0.4)
        gs = fig.add_gridspec(3, 3, height_ratios=[1, 1.2, 1.2])
        
        # Title
        ax_title = fig.add_subplot(gs[0, :])
        ax_title.axis('off')
        ax_title.text(0.5, 0.65, 'İsmi En Çok Geçen',
                      ha='center', va='center', fontsize=46, fontweight='bold',
                      color='#E74C3C')
        ax_title.text(0.5, 0.35, 'Kim kimden ne kadar bahsediyor?',
                      ha='center', va='center', fontsize=20,
                      color='#444444', style='italic')
        
        # Most Mentioned Person
        ax_mentioned = fig.add_subplot(gs[1, 0])
        ax_mentioned.axis('off')
        ax_mentioned.text(0.5, 0.85, 'EN ÇOK BAHSEDİLEN',
                          ha='center', va='center', fontsize=18, fontweight='bold',
                          color='#C0392B')
        if most_mentioned[0]:
            ax_mentioned.text(0.5, 0.55, most_mentioned[0],
                            ha='center', va='center', fontsize=32, fontweight='bold',
                            color='#E74C3C')
            ax_mentioned.text(0.5, 0.28, f'{most_mentioned[1]} kez',
                            ha='center', va='center', fontsize=20,
                            color='#34495e')
            ax_mentioned.text(0.5, 0.10, 'Konuşmaların merkezi!',
                            ha='center', va='center', fontsize=12,
                            color='#555555', style='italic')
        
        # Most Active Mentioner
        ax_mentioner = fig.add_subplot(gs[1, 1])
        ax_mentioner.axis('off')
        ax_mentioner.text(0.5, 0.85, 'EN ÇOK BAHSEDEN',
                          ha='center', va='center', fontsize=18, fontweight='bold',
                          color='#C0392B')
        if most_mentioner[0]:
            ax_mentioner.text(0.5, 0.55, most_mentioner[0],
                            ha='center', va='center', fontsize=32, fontweight='bold',
                            color='#E74C3C')
            ax_mentioner.text(0.5, 0.28, f'{most_mentioner[1]} kez',
                            ha='center', va='center', fontsize=20,
                            color='#34495e')
            ax_mentioner.text(0.5, 0.10, 'İsimleri seviyor!',
                            ha='center', va='center', fontsize=12,
                            color='#555555', style='italic')
        
        # Strongest Link
        ax_link = fig.add_subplot(gs[1, 2])
        ax_link.axis('off')
        ax_link.text(0.5, 0.90, 'EN BÜYÜK FANI',
                      ha='center', va='center', fontsize=18, fontweight='bold',
                      color='#C0392B')
        if strongest_link[0]:
            ax_link.text(0.5, 0.72, strongest_link[0],
                        ha='center', va='center', fontsize=24, fontweight='bold',
                        color='#E74C3C')
            ax_link.text(0.5, 0.55, 'bu kişiden çok bahsediyor:',
                        ha='center', va='center', fontsize=12,
                        color='#444444', style='italic')
            ax_link.text(0.5, 0.45, '↓',
                        ha='center', va='center', fontsize=28,
                        color='#444444')
            ax_link.text(0.5, 0.22, strongest_link[1],
                        ha='center', va='center', fontsize=24, fontweight='bold',
                        color='#E74C3C')
            ax_link.text(0.5, 0.08, f'{strongest_link[2]} kez bahsetti',
                        ha='center', va='center', fontsize=16,
                        color='#34495e')
        
        # Top Mentions Bar Chart
        ax_chart = fig.add_subplot(gs[2, :])
        
        # Adjust position to move right (shrink from left)
        pos = ax_chart.get_position()
        ax_chart.set_position([pos.x0 + 0.2, pos.y0, pos.width - 0.2, pos.height])
        
        if total_mentions_received:
            sorted_mentions = sorted(total_mentions_received.items(), key=lambda x: x[1], reverse=True)[:6]
            names = [x[0] for x in sorted_mentions]
            counts = [x[1] for x in sorted_mentions]
            
            colors = ['#E74C3C' if i == 0 else '#EC7063' for i in range(len(names))]
            bars = ax_chart.barh(range(len(names)), counts, color=colors, edgecolor='black')
            ax_chart.set_yticks(range(len(names)))
            ax_chart.set_yticklabels(names, fontsize=14)
            ax_chart.set_xlabel('Toplam Bahsedilme Sayısı', fontsize=14, fontweight='bold')
            ax_chart.grid(axis='x', linestyle='--', alpha=0.3)
            ax_chart.invert_yaxis()
            
            # Add count labels
            for i, (bar, count) in enumerate(zip(bars, counts)):
                ax_chart.text(count + max(counts) * 0.01, i, f'{count}',
                            va='center', fontsize=12, fontweight='bold')
        
        self._add_footer(fig)
        pdf.savefig(fig)
        plt.close()
    
    def create_streak_slide(self, pdf):
        """Slide: Longest silence and daily message streaks"""
        from datetime import timedelta
        
        # Sort by timestamp
        df_sorted = self.chat_df.sort_values('timestamp').copy()
        
        # Calculate longest silence for each user
        longest_silence = {}
        daily_streaks = {}
        
        for user in df_sorted['sender'].unique():
            user_msgs = df_sorted[df_sorted['sender'] == user]['timestamp'].reset_index(drop=True)
            
            # Longest silence
            if len(user_msgs) > 1:
                time_diffs = user_msgs.diff().dropna()
                max_gap = time_diffs.max()
                longest_silence[user] = max_gap.total_seconds() / 86400  # Convert to days
            else:
                longest_silence[user] = 0
            
            # Daily streak (consecutive days with at least 1 message)
            if len(user_msgs) > 0:
                msg_dates = user_msgs.dt.date.unique()
                msg_dates_sorted = sorted(msg_dates)
                
                current_streak = 1
                max_streak = 1
                
                for i in range(1, len(msg_dates_sorted)):
                    if (msg_dates_sorted[i] - msg_dates_sorted[i-1]).days == 1:
                        current_streak += 1
                        max_streak = max(max_streak, current_streak)
                    else:
                        current_streak = 1
                
                daily_streaks[user] = max_streak
            else:
                daily_streaks[user] = 0
        
        # Find champions
        silence_champion = max(longest_silence.items(), key=lambda x: x[1]) if longest_silence else (None, 0)
        streak_champion = max(daily_streaks.items(), key=lambda x: x[1]) if daily_streaks else (None, 0)
        
        fig = plt.figure(figsize=(16, 9))
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        gs = fig.add_gridspec(3, 2, height_ratios=[1, 1.5, 1.5], wspace=0.4)
        
        # Title
        ax_title = fig.add_subplot(gs[0, :])
        ax_title.axis('off')
        ax_title.text(0.5, 0.65, 'Streak Rekorları',
                      ha='center', va='center', fontsize=46, fontweight='bold',
                      color='#9B59B6')
        ax_title.text(0.5, 0.35, 'En uzun sessizlik vs. En uzun seri',
                      ha='center', va='center', fontsize=20,
                      color='#444444', style='italic')
        
        # Longest Silence Champion
        ax_silence = fig.add_subplot(gs[1, 0])
        ax_silence.axis('off')
        ax_silence.text(0.5, 0.90, 'EN UZUN SESSİZLİK',
                       ha='center', va='center', fontsize=20, fontweight='bold',
                       color='#7D3C98')
        if silence_champion[0]:
            ax_silence.text(0.5, 0.62, silence_champion[0],
                          ha='center', va='center', fontsize=34, fontweight='bold',
                          color='#9B59B6')
            ax_silence.text(0.5, 0.38, f'{silence_champion[1]:.1f} gün',
                          ha='center', va='center', fontsize=28,
                          color='#34495e')
            ax_silence.text(0.5, 0.15, 'Yeni arkadaşlar mı buldun?',
                          ha='center', va='center', fontsize=13,
                          color='#555555', style='italic')
        
        # Daily Streak Champion
        ax_streak = fig.add_subplot(gs[1, 1])
        ax_streak.axis('off')
        ax_streak.text(0.5, 0.90, 'EN UZUN GÜNLÜK SERİ',
                       ha='center', va='center', fontsize=20, fontweight='bold',
                       color='#7D3C98')
        if streak_champion[0]:
            ax_streak.text(0.5, 0.62, streak_champion[0],
                         ha='center', va='center', fontsize=34, fontweight='bold',
                         color='#9B59B6')
            ax_streak.text(0.5, 0.38, f'{int(streak_champion[1])} gün',
                         ha='center', va='center', fontsize=28,
                         color='#34495e')
            ax_streak.text(0.5, 0.15, 'Günde en az 1 mesaj!',
                         ha='center', va='center', fontsize=13,
                         color='#555555', style='italic')
        
        # Silence comparison chart
        ax_silence_chart = fig.add_subplot(gs[2, 0])
        
        # Shift right
        pos = ax_silence_chart.get_position()
        ax_silence_chart.set_position([pos.x0 + 0.06, pos.y0, pos.width - 0.06, pos.height])
        
        if longest_silence:
            sorted_silence = sorted(longest_silence.items(), key=lambda x: x[1], reverse=True)[:6]
            names = [x[0] for x in sorted_silence]
            days = [x[1] for x in sorted_silence]
            
            colors = ['#9B59B6' if i == 0 else '#BB8FCE' for i in range(len(names))]
            bars = ax_silence_chart.barh(range(len(names)), days, color=colors, edgecolor='black')
            ax_silence_chart.set_yticks(range(len(names)))
            ax_silence_chart.set_yticklabels(names, fontsize=12)
            ax_silence_chart.set_xlabel('En Uzun Sessizlik (Gün)', fontsize=12, fontweight='bold')
            ax_silence_chart.grid(axis='x', linestyle='--', alpha=0.3)
            ax_silence_chart.invert_yaxis()
            
            for i, (bar, day) in enumerate(zip(bars, days)):
                ax_silence_chart.text(day + max(days) * 0.01, i, f'{day:.1f}',
                                     va='center', fontsize=11, fontweight='bold')
        
        # Streak comparison chart
        ax_streak_chart = fig.add_subplot(gs[2, 1])
        
        # Shift right
        pos = ax_streak_chart.get_position()
        ax_streak_chart.set_position([pos.x0 + 0.06, pos.y0, pos.width - 0.06, pos.height])
        
        if daily_streaks:
            sorted_streaks = sorted(daily_streaks.items(), key=lambda x: x[1], reverse=True)[:6]
            names = [x[0] for x in sorted_streaks]
            streaks = [x[1] for x in sorted_streaks]
            
            colors = ['#9B59B6' if i == 0 else '#BB8FCE' for i in range(len(names))]
            bars = ax_streak_chart.barh(range(len(names)), streaks, color=colors, edgecolor='black')
            ax_streak_chart.set_yticks(range(len(names)))
            ax_streak_chart.set_yticklabels(names, fontsize=12)
            ax_streak_chart.set_xlabel('En Uzun Günlük Seri (Gün)', fontsize=12, fontweight='bold')
            ax_streak_chart.grid(axis='x', linestyle='--', alpha=0.3)
            ax_streak_chart.invert_yaxis()
            
            for i, (bar, streak) in enumerate(zip(bars, streaks)):
                ax_streak_chart.text(streak + max(streaks) * 0.01, i, f'{int(streak)}',
                                    va='center', fontsize=11, fontweight='bold')
        
        self._add_footer(fig)
        pdf.savefig(fig)
        plt.close()

    def create_unique_words_slide(self, pdf):
        """Slide: Unique Word Usage (Keyness Analysis)"""
        from collections import defaultdict
        import numpy as np
        
        # Stop words (same as top_words_slide)
        stop_words = {
            've', 'bir', 'bu', 'da', 'de', 'mi', 'mu', 'mü', 'için', 'ile', 'o', 'ne', 'var', 
            'ya', 'çok', 'ben', 'sen', 'biz', 'siz', 'onlar', 'daha', 'en', 'şey', 'gibi',
            'ama', 'veya', 'olan', 'oldu', 'yok', 'ki', 'mı', 'nasıl', 'neden', 'nerede',
            'kim', 'şimdi', 'sonra', 'var', 'yani', 'falan', 'işte', 'hani', 'böyle', 'öyle',
            'şu', 'bana', 'sana', 'ona', 'bunu', 'şunu', 'onu', 'the', 'a', 'an', 'and', 'or',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do',
            'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'to',
            'message', 'deleted', 'omitted', 'media', 'image', 'video', 'audio', 'sticker',
            'document', 'contact', 'location', 'null', 'undefined', 'edited'
        }
        
        # Build word frequency per sender (Vectorized)
        # 1. Pre-process text: Lowercase and remove punctuation
        clean_content = self.chat_df['content'].astype(str).str.lower().str.replace(r'[^\w\s]', '', regex=True)
        
        # 2. Explode into words (Sender -> Word mapping)
        # stack() creates a MultiIndex, we drop the inner level to align with sender index
        stacked_words = clean_content.str.split(expand=True).stack()
        
        # Join with sender column (using the index)
        df_words = self.chat_df[['sender']].join(
            stacked_words.reset_index(level=1, drop=True).rename('word')
        )
        
        # 3. Filter words
        # Length >= 3
        df_words = df_words[df_words['word'].str.len() >= 3]
        # Check against stop words
        df_words = df_words[~df_words['word'].isin(stop_words)]
        
        if df_words.empty:
            return
            
        # 4. Create Frequency Matrix (Rows: Senders, Cols: Words)
        word_counts = pd.crosstab(df_words['sender'], df_words['word'])
        
        # 5. Calculate Keyness Scores (Vectorized Log-Likelihood)
        observed = word_counts.values
        row_totals = observed.sum(axis=1)[:, None] # Sender totals
        col_totals = observed.sum(axis=0)[None, :] # Word totals
        grand_total = observed.sum()
        
        # Expected frequencies
        expected = (row_totals @ col_totals) / grand_total
        
        # Log-Likelihood Ratio
        with np.errstate(divide='ignore', invalid='ignore'):
            lli = 2 * observed * np.log(observed / expected)
        
        # Filter: Only check positive associations (Observed > Expected)
        lli[observed <= expected] = 0
        lli[~np.isfinite(lli)] = 0
        
        # 6. Winner Takes All (Global Uniqueness Logic)
        scores_df = pd.DataFrame(lli, index=word_counts.index, columns=word_counts.columns)
        
        # Identify the max score owner for each word
        word_winners = scores_df.idxmax(axis=0)
        
        unique_words_per_sender = {}
        
        for sender in scores_df.index:
            # Get words where this sender is the winner
            won_words_mask = (word_winners == sender)
            
            if not won_words_mask.any():
                continue
                
            # Get the scores for these words
            my_scores = scores_df.loc[sender, won_words_mask]
            
            # Sort by score descending and take top 3
            top_3 = my_scores.sort_values(ascending=False).head(3)
            
            if not top_3.empty:
                unique_words_per_sender[sender] = list(zip(top_3.index, top_3.values))
        
        if len(unique_words_per_sender) == 0:
            return
        
        fig = plt.figure(figsize=(16, 9))
        gs = fig.add_gridspec(3, 1, height_ratios=[1, 0.2, 2.8])
        
        # Title
        ax_title = fig.add_subplot(gs[0])
        ax_title.axis('off')
        ax_title.text(0.5, 0.65, 'Kendine Özgü Kelimeler',
                      ha='center', va='center', fontsize=46, fontweight='bold',
                      color='#16A085')
        ax_title.text(0.5, 0.35, 'Herkesin kendine özgü imza kelimeleri!',
                      ha='center', va='center', fontsize=20,
                      color='#444444', style='italic')
        
        # Spacer
        ax_spacer = fig.add_subplot(gs[1])
        ax_spacer.axis('off')
        
        # Create grid for users
        ax_grid = fig.add_subplot(gs[2])
        ax_grid.axis('off')
        
        # Calculate grid layout
        n_users = len(unique_words_per_sender)
        cols = min(3, n_users)
        rows = (n_users + cols - 1) // cols
        
        colors = ['#1ABC9C', '#16A085', '#27AE60', '#2ECC71', '#3498DB', '#2980B9']
        
        for idx, (sender, words) in enumerate(unique_words_per_sender.items()):
            row = idx // cols
            col = idx % cols
            
            # Calculate position with better margins
            slot_width = 1.0 / cols
            width = slot_width * 0.9
            left = col * slot_width + (slot_width - width) / 2
            
            slot_height = 1.0 / rows
            height = slot_height * 0.85
            bottom = 1.0 - (row + 1) * slot_height + (slot_height - height) / 2
            
            # Create box
            from matplotlib.patches import FancyBboxPatch
            box_color = colors[idx % len(colors)]
            
            # Draw sender name
            ax_grid.text(left + width/2, bottom + height * 0.85, sender,
                        ha='center', va='center', fontsize=18, fontweight='bold',
                        color=box_color, transform=ax_grid.transAxes)
            
            # Draw unique words
            word_y_positions = [0.65, 0.45, 0.25]
            for i, (word, score) in enumerate(words):
                if i < 3:
                    ax_grid.text(left + width/2, bottom + height * word_y_positions[i],
                                f'• {word}',
                                ha='center', va='center', fontsize=16,
                                color='#2C3E50', transform=ax_grid.transAxes,
                                style='italic')
            
            # Draw box border
            rect = FancyBboxPatch((left, bottom), width * 0.92, height * 0.92,
                                 boxstyle="round,pad=0.01", 
                                 edgecolor=box_color, facecolor='none',
                                 linewidth=2.5, transform=ax_grid.transAxes,
                                 alpha=0.7)
            ax_grid.add_patch(rect)
        
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        self._add_footer(fig)
        pdf.savefig(fig)
        plt.close()
    
    def create_weekly_champions_slide(self, pdf):
        """Slide: Weekly Champions"""
        most_messages_weekly = self.chat_df.groupby(
            [pd.Grouper(key='timestamp', freq='W'), 'sender']
        ).size().reset_index(name='message_count')
        
        weekly_winners = most_messages_weekly.loc[
            most_messages_weekly.groupby('timestamp')['message_count'].idxmax()
        ]
        
        # Count wins per person
        win_counts = weekly_winners['sender'].value_counts()
        
        if len(win_counts) == 0:
            return
        
        winner = win_counts.index[0]
        winner_weeks = win_counts.iloc[0]
        
        fig = plt.figure(figsize=(16, 9))
        gs = fig.add_gridspec(2, 2, height_ratios=[1, 2])
        
        # Title
        ax_title = fig.add_subplot(gs[0, :])
        ax_title.axis('off')
        ax_title.text(0.5, 0.65, 'Haftalık Mesaj Şampiyonu',
                      ha='center', va='center', fontsize=46, fontweight='bold',
                      color='#FFD700')
        ax_title.text(0.5, 0.35, 'Mesaj sayısında en çok hafta birinciliği kazanan!',
                      ha='center', va='center', fontsize=20,
                      color='#444444', style='italic')
        
        # Winner
        ax_winner = fig.add_subplot(gs[1, 0])
        ax_winner.axis('off')
        ax_winner.text(0.5, 0.65, winner,
                      ha='center', va='center', fontsize=52, fontweight='bold',
                      color='#FFA500')
        ax_winner.text(0.5, 0.40, f'{winner_weeks} hafta\nEn aktif',
                      ha='center', va='center', fontsize=26,
                      color='#34495e')
        ax_winner.text(0.5, 0.20, 'İstikrar bu olsa gerek!',
                      ha='center', va='center', fontsize=16,
                      color='#555555', style='italic')
        
        # Chart
        ax_chart = fig.add_subplot(gs[1, 1])
        n_users = len(win_counts)
        top_users = win_counts.head(5) if n_users >= 7 else win_counts
        colors = ['#FFD700' if i == 0 else '#87CEEB' for i in range(len(top_users))]
        ax_chart.barh(range(len(top_users)), top_users.values, color=colors, edgecolor='black')
        ax_chart.set_yticks(range(len(top_users)))
        ax_chart.set_yticklabels(top_users.index, fontsize=14)
        ax_chart.set_xlabel('Kazanılan Hafta Sayısı', fontsize=14, fontweight='bold')
        ax_chart.grid(axis='x', linestyle='--', alpha=0.3)
        ax_chart.invert_yaxis()
        
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        self._add_footer(fig)
        pdf.savefig(fig)
        plt.close()
        
    def create_weekly_timeline_slide(self, pdf):
        """Slide: Weekly Winners Timeline"""
        
        # Group by week and find winner of each week
        most_messages_weekly = self.chat_df.groupby(
            [pd.Grouper(key='timestamp', freq='W'), 'sender']
        ).size().reset_index(name='message_count')
        
        weekly_winners = most_messages_weekly.loc[
            most_messages_weekly.groupby('timestamp')['message_count'].idxmax()
        ]
        
        if len(weekly_winners) == 0:
            return
        
        # Get unique senders and assign colors
        unique_senders = weekly_winners['sender'].unique()
        
        # Use a high-contrast colormap for better distinction
        cmap = plt.get_cmap('tab20')
        color_map = {sender: cmap(i % 20) for i, sender in enumerate(unique_senders)}
        
        fig = plt.figure(figsize=(16, 9))
        gs = fig.add_gridspec(2, 1, height_ratios=[1, 4])
        
        # Title
        ax_title = fig.add_subplot(gs[0])
        ax_title.axis('off')
        ax_title.text(0.5, 0.65, 'Haftalık En Çok Mesaj Atanlar Çizelgesi',
                      ha='center', va='center', fontsize=46, fontweight='bold',
                      color='#2C3E50')
        ax_title.text(0.5, 0.35, 'Her hafta en aktif olan kişi',
                      ha='center', va='center', fontsize=20,
                      color='#444444', style='italic')
        
        # Timeline chart
        ax_chart = fig.add_subplot(gs[1])
        
        # Create vertical bar chart grouped by sender
        for sender in unique_senders:
            sender_data = weekly_winners[weekly_winners['sender'] == sender]
            ax_chart.bar(sender_data['timestamp'], sender_data['message_count'], 
                        color=color_map[sender], label=sender, width=5, edgecolor='black', linewidth=0.5)
        
        # Set labels and styling
        ax_chart.set_xlabel('Hafta', fontsize=14, fontweight='bold')
        ax_chart.set_ylabel('Mesaj Sayısı', fontsize=14, fontweight='bold')
        ax_chart.tick_params(axis='x', rotation=45, labelsize=10)
        ax_chart.tick_params(axis='y', labelsize=10)
        ax_chart.legend(title='Kişiler', fontsize=11, title_fontsize=12, framealpha=0.9)
        ax_chart.grid(color='#BDC3C7', linestyle='--', linewidth=0.5, alpha=0.7)
        
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.15)
        self._add_footer(fig)
        pdf.savefig(fig)
        plt.close()
    
    def create_conversation_continuation_slide(self, pdf):
        """Slide: Average Continuation of Start Messages"""
        # Create a working copy with reset index to calculate message counts correctly
        df_working = self.chat_df.copy().reset_index(drop=True)
        
        # Filter rows with is_start as True
        start_messages = df_working[df_working['is_start']].copy()
        
        if len(start_messages) == 0:
            return

        # Calculate the number of messages until the next start message
        start_messages['next_start_index'] = start_messages.index.to_series().shift(-1)
        # Fill NaN for the last start message with the length of the dataframe
        start_messages['next_start_index'] = start_messages['next_start_index'].fillna(len(df_working))
        
        start_messages['messages_until_next_start'] = start_messages['next_start_index'] - start_messages.index

        # Group by sender and calculate the average
        continuation_analysis = start_messages.groupby('sender')['messages_until_next_start'].mean().sort_values(ascending=False)
        
        if len(continuation_analysis) == 0:
            return
            
        winner = continuation_analysis.index[0]
        winner_avg = continuation_analysis.iloc[0]
        
        fig = plt.figure(figsize=(16, 9))
        gs = fig.add_gridspec(2, 2, height_ratios=[1, 2], wspace=0.3)
        
        # Title
        ax_title = fig.add_subplot(gs[0, :])
        ax_title.axis('off')
        ax_title.text(0.5, 0.65, 'Konuşma Sürdürme',
                      ha='center', va='center', fontsize=46, fontweight='bold',
                      color='#2E86C1')
        ax_title.text(0.5, 0.35, 'Başlattığı konular ne kadar uzuyor?',
                      ha='center', va='center', fontsize=20,
                      color='#444444', style='italic')
        
        # Winner
        ax_winner = fig.add_subplot(gs[1, 0])
        ax_winner.axis('off')
        ax_winner.text(0.5, 0.65, winner,
                      ha='center', va='center', fontsize=52, fontweight='bold',
                      color='#1B4F72')
        ax_winner.text(0.5, 0.40, f'Ortalama {winner_avg:.1f} mesaj',
                      ha='center', va='center', fontsize=26,
                      color='#34495e')
        ax_winner.text(0.5, 0.20, 'Konuyu açtı mı kapatamıyoruz!',
                      ha='center', va='center', fontsize=16,
                      color='#555555', style='italic')
        
        # Chart
        ax_chart = fig.add_subplot(gs[1, 1])
        n_users = len(continuation_analysis)
        top_users = continuation_analysis.head(5) if n_users >= 7 else continuation_analysis
        colors = ['#2E86C1' if i == 0 else '#85C1E9' for i in range(len(top_users))]
        ax_chart.barh(range(len(top_users)), top_users.values, color=colors, edgecolor='black')
        ax_chart.set_yticks(range(len(top_users)))
        ax_chart.set_yticklabels(top_users.index, fontsize=14)
        ax_chart.set_xlabel('Ortalama Mesaj Sayısı', fontsize=14, fontweight='bold')
        ax_chart.grid(axis='x', linestyle='--', alpha=0.3)
        ax_chart.invert_yaxis()
        
        # Add labels
        for i, val in enumerate(top_users.values):
            ax_chart.text(val + max(top_users.values) * 0.02, i, f'{val:.1f}',
                         va='center', ha='left', fontsize=12, fontweight='bold', color='#34495e')
        
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        self._add_footer(fig)
        pdf.savefig(fig)
        plt.close()
    
    def create_profanity_slide(self, pdf):
        """Slide: Profanity Champion (if blacklist provided)"""
        if not self.blacklist_words:
            return
        
        import re
        
        # Optimize: Use vectorized string operations instead of apply
        # Calculate total words first (vectorized)
        # We perform lower() once for the whole column
        content_lower = self.chat_df['content'].str.lower()
        self.chat_df['total_words'] = content_lower.str.split().str.len()
        
        # Create a maximized regex pattern for blacklist
        # Sort by length descending to match longer phrases first (e.g. "amcik hosafi" before "amcik")
        sorted_blacklist = sorted(self.blacklist_words, key=len, reverse=True)
        escaped_words = [re.escape(w) for w in sorted_blacklist]
        pattern = r'\b(?:' + '|'.join(escaped_words) + r')\b'
        
        # Vectorized count
        self.chat_df['blacklist_count'] = content_lower.str.count(pattern)
        
        # Calculate profanity density per sender
        profanity_stats = self.chat_df.groupby('sender').agg({
            'blacklist_count': 'sum',
            'total_words': 'sum'
        })
        
        # Calculate density (words per profanity)
        profanity_stats['words_per_profanity'] = profanity_stats['total_words'] / profanity_stats['blacklist_count']
        profanity_stats = profanity_stats[profanity_stats['blacklist_count'] > 0].sort_values('words_per_profanity')
        
        if len(profanity_stats) == 0:
            return
        
        winner = profanity_stats.index[0]
        winner_ratio = profanity_stats.loc[winner, 'words_per_profanity']
        winner_count = int(profanity_stats.loc[winner, 'blacklist_count'])
        
        fig = plt.figure(figsize=(16, 9))
        gs = fig.add_gridspec(2, 2, height_ratios=[1, 2])
        
        # Title
        ax_title = fig.add_subplot(gs[0, :])
        ax_title.axis('off')
        ax_title.text(0.5, 0.65, 'Kötü Söz Yoğunluğu',
                      ha='center', va='center', fontsize=46, fontweight='bold',
                      color='#DC143C')
        ax_title.text(0.5, 0.35, 'Her kaç kelimede bir kötü söz kullanıyor?',
                      ha='center', va='center', fontsize=20,
                      color='#444444', style='italic')
        
        # Winner
        ax_winner = fig.add_subplot(gs[1, 0])
        ax_winner.axis('off')
        ax_winner.text(0.5, 0.70, winner,
                      ha='center', va='center', fontsize=52, fontweight='bold',
                      color='#8B0000')
        ax_winner.text(0.5, 0.48, f'Her {winner_ratio:.1f} kelimede',
                      ha='center', va='center', fontsize=24,
                      color='#34495e')
        ax_winner.text(0.5, 0.35, f'1 kötü söz!',
                      ha='center', va='center', fontsize=28, fontweight='bold',
                      color='#8B0000')
        ax_winner.text(0.5, 0.18, f'(Toplam {winner_count} kötü söz)',
                      ha='center', va='center', fontsize=16,
                      color='#555555', style='italic')
        
        # Chart - Lower is worse (more profanity)
        ax_chart = fig.add_subplot(gs[1, 1])
        n_users = len(profanity_stats)
        top_users = profanity_stats.head(5) if n_users >= 7 else profanity_stats
        colors = ['#DC143C' if i == 0 else '#CD5C5C' for i in range(len(top_users))]
        ax_chart.barh(range(len(top_users)), top_users['words_per_profanity'].values, color=colors, edgecolor='black')
        ax_chart.set_yticks(range(len(top_users)))
        ax_chart.set_yticklabels(top_users.index, fontsize=14)
        ax_chart.set_xlabel('Kaç Kelimede 1 Kötü Söz', fontsize=14, fontweight='bold')
        ax_chart.grid(axis='x', linestyle='--', alpha=0.3)
        ax_chart.invert_yaxis()
        # Set x-axis limits to make room for labels on the left (max value side)
        max_val = max(top_users['words_per_profanity'])
        ax_chart.set_xlim(max_val * 1.15, 0)  # Inverted axis: max on left, 0 on right
        
        # Add ratio labels on bars (outside, on the left)
        for i, (idx, row) in enumerate(top_users.iterrows()):
            ratio = row['words_per_profanity']
            ax_chart.text(ratio + max_val * 0.01, i, f'{ratio:.1f}',
                         va='center', ha='right', fontsize=12, fontweight='bold', color='#34495e')
        
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        self._add_footer(fig)
        pdf.savefig(fig)
        plt.close()
    
    def create_weekly_champion_slide(self, pdf):
        """Slide: Weekly Champion Timeline"""
        import matplotlib.dates as mdates
        
        # Resample by week
        weekly_stats = self.chat_df.groupby([pd.Grouper(key='timestamp', freq='W-MON'), 'sender']).size().unstack(fill_value=0)
        
        if weekly_stats.empty:
            return
            
        weekly_winners = weekly_stats.idxmax(axis=1)
        weekly_totals = weekly_stats.sum(axis=1)
        
        # Colors
        users = sorted(self.chat_df['sender'].unique())
        colors_palette = ['#3498DB', '#E74C3C', '#F1C40F', '#9B59B6', '#2ECC71', '#E67E22', '#1ABC9C']
        user_colors = {u: colors_palette[i % len(colors_palette)] for i, u in enumerate(users)}
        
        # Calculate overall champion
        win_counts = weekly_winners.value_counts()
        champion = win_counts.index[0]
        champion_wins = win_counts.iloc[0]
        
        fig = plt.figure(figsize=(16, 9))
        gs = fig.add_gridspec(2, 1, height_ratios=[1, 3])
        
        # Title
        ax_title = fig.add_subplot(gs[0])
        ax_title.axis('off')
        ax_title.text(0.5, 0.65, 'Haftalık Şampiyonluklar', ha='center', va='center', fontsize=46, fontweight='bold', color='#F39C12')
        ax_title.text(0.5, 0.35, f'Toplam {champion_wins} hafta ile Lider: {champion}!', ha='center', va='center', fontsize=20, color='#444444', style='italic')

        # Chart
        ax_chart = fig.add_subplot(gs[1])
        
        dates = weekly_stats.index
        bar_colors = [user_colors.get(weekly_winners[d], '#999') for d in dates]
        
        # Plot bars
        ax_chart.bar(dates, weekly_totals, width=5, color=bar_colors, alpha=0.9, edgecolor='white', linewidth=0.5)
        
        # Formatting
        ax_chart.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
        ax_chart.xaxis.set_major_locator(mdates.MonthLocator())
        
        ax_chart.set_ylabel('Mesaj Sayısı', fontsize=12, fontweight='bold', color='#555')
        ax_chart.grid(axis='y', linestyle='--', alpha=0.3)
        ax_chart.spines['top'].set_visible(False)
        ax_chart.spines['right'].set_visible(False)
        
        # Custom Legend
        import matplotlib.patches as mpatches
        legend_handles = [mpatches.Patch(color=user_colors[u], label=u) for u in users]
        ax_chart.legend(handles=legend_handles, loc='upper right', frameon=False, fontsize=12)
        
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        self._add_footer(fig)
        pdf.savefig(fig)
        plt.close()
    def create_calculation_explanation_slide(self, pdf):
        """Create a slide explaining how each calculation is made"""
        fig = plt.figure(figsize=(16, 9))
        
        # Title area - moved up slightly and reduced height
        ax_title = fig.add_axes([0, 0.92, 1, 0.08])
        ax_title.axis('off')
        ax_title.text(0.5, 0.5, 'Hesaplamalar Nasıl Yapıldı?',
                ha='center', va='center', fontsize=32, fontweight='bold',
                color='#2C3E50')
        
        # Main content area - shrunk vertically to avoid overlap
        # [left, bottom, width, height]
        # Increased bottom margin from 0.06 to 0.12 to clear the footer
        ax = fig.add_axes([0.05, 0.12, 0.9, 0.78])
        ax.axis('off')
        
        # Explanations - organized in two columns based on Mode
        if getattr(self, 'is_dm', False):
             explanations = [
                ('Mesaj Sayısı Dengesi', 'Toplam mesajların yüzde kaçının hangi taraftan gönderildiği.'),
                ('Günün İlk Mesajını En Çok Atan', 'Saat 06:00\'dan sonraki günün ilk mesajını en çok gönderen kişi.'),
                ('Mesaja Dönme Hızı', 'Karşı tarafın mesajına ortalama cevap verme süresi (24 saati aşmayanlar).'),
                ('Konuşma Başlatan', '1 saatten fazla sessizlikten sonra ilk mesajı gönderen kişi sayısı.'),
                ('En Uzun Mesajlaşma Günü', 'Bir gün içinde karşılıklı en çok mesaj atılan gün.'),
                ('En Yoğun Saat', 'İkinizin toplamda en çok mesajlaştığı saat dilimi (Örn: 22:00-23:00).'),
                ('Sessizlik Haritası', 'Günün en az mesaj gönderilen 3 saatlik dilimi.'),
                ('Sohbet Ritmi', 'Zaman içindeki (haftalık) mesajlaşma yoğunluğu.'),
                ('En Uzun Mesajları Yazan', 'Ortalama mesaj uzunluğu (karakter) en yüksek olan kişi.'),
                ('En Çok Kullanılan Kelimeler', 'En sık kullanılan kelimeler (bağlaçlar hariç).'),
                ('Emoji & Noktalama', 'En çok emoji ve noktalama işareti kullanan kişiler.'),
                ('Seriler (Streaks)', 'Hiç ara vermeden en uzun süre (gün) mesajlaşılan dönem.'),
                ('Kendine Özgü Kelimeler', 'Diğer kişiye kıyasla daha sık kullanılan kelimeler.'),
                ('Kötü Söz Yoğunluğu', 'Sansürlü kelime listesindeki kelimelerin kullanım sıklığı.'),
                ('En Çok Bağıran', 'Tamamı büyük harflerden oluşan mesaj sayısı en yüksek kişi.'),
                ('Haftalık Şampiyon', 'Her hafta en çok mesaj gönderen kişi (Haftanın Rengi).'),
            ]
        else:
            explanations = [
                ('Grubun En Aktifi', 'Toplam mesaj sayısına göre en çok mesaj gönderen kişi.'),
                ('Gece Kuşu', 'Saat 00:00-05:00 arası en çok mesaj gönderen kişi.'),
                ('Günün İlk Mesajı', 'Saat 06:00\'dan sonraki günün ilk mesajını en çok gönderen kişi.'),
                ('Sabah İlk Cevap Veren', 'Günün ilk mesajından sonra ilk cevap veren kişi.'),
                ('Konuşma Başlatan', '1 saatten fazla sessizlikten sonra ilk mesaj gönderen kişi.'),
                ('İlk Cevap Veren', 'Konuşma başlatandan farklı, hemen sonra mesaj gönderen kişi.'),
                ('Konuşma Sürdürme', 'Başlattığı konuşmaların ortalama kaç mesaj sürdüğü.'),
                ('En Uzun Mesajları Yazan', 'Ortalama mesaj uzunluğu (karakter) en yüksek olan kişi.'),
                ('En Yoğun Saat', 'Grubun en çok mesaj gönderdiği saat dilimi.'),
                ('En Çok Kullanılan Kelimeler', 'En sık kullanılan kelimeler (bağlaçlar hariç).'),
                ('Emoji & Noktalama', 'En çok emoji ve noktalama işareti kullanan kişiler.'),
                ('En Çok Etkileşimde Olan İkililer', 'Araya başkası girmeden en az 5 mesaj süren konuşmalar.'),
                ('İsmi En Çok Geçen', 'Mesajlarda ismi en çok bahsedilen ve en çok bahsedenler.'),
                ('En Uzun Sessizlik', 'İki mesajı arasında en uzun süre geçen kişi (gün).'),
                ('En Uzun Günlük Seri', 'Ardışık günlerde en az 1 mesaj gönderen kişi (gün).'),
                ('Kendine Özgü Kelimeler', 'Diğerlerine kıyasla daha sık kullandığı kelimeler.'),
                ('Kötü Söz Yoğunluğu', 'Kaç kelimede bir kötü söz kullanıldığı.'),
                ('Haftalık Şampiyon', 'Haftalık mesaj sayısında en çok birinci olan kişi.'),
                ('Grup Aktivite Grafiği', 'Yıl boyunca haftalık mesaj sayısı dağılımı.'),
                ('En Çok Bağıran', 'Tamamı büyük harflerden oluşan mesaj sayısı en yüksek kişi.'),
            ]
        
        # Layout settings
        items_per_col = 10
        row_height = 1.0 / items_per_col
        
        for i, (title, desc) in enumerate(explanations):
            col = i // items_per_col
            row = i % items_per_col
            
            # Calculate position
            x = 0.02 + (col * 0.5)
            y = 0.98 - (row * row_height)
            
            # Title - Smaller font
            ax.text(x, y, title + ":",
                   ha='left', va='top', fontsize=11, fontweight='bold',
                   color='#2980B9')
            
            # Description - Smaller font and adjusted position
            ax.text(x, y - 0.035, desc,
                   ha='left', va='top', fontsize=9,
                   color='#34495e', wrap=True)
                   
            # Add a light separator line (except for the last item in column)
            if row < items_per_col - 1:
                ax.plot([x, x + 0.45], [y - 0.08, y - 0.08], color='#BDC3C7', linewidth=0.5, alpha=0.3)

        # Footer note - Smaller font
        fig.text(0.5, 0.045, 'Not: Tüm hesaplamalar 1 Aralık 2024 - 1 Aralık 2025 tarihleri arasındaki mesajlar üzerinden yapılmıştır.',
                ha='center', va='bottom', fontsize=9,
                color='#444444', style='italic')
        
        self._add_footer(fig)
        pdf.savefig(fig)
        plt.close()
    
    def create_closing_slide(self, pdf):
        """Create a closing slide"""
        fig, ax = plt.subplots(figsize=(16, 9))
        ax.axis('off')
        
        # Main message
        ax.text(0.5, 0.6, 'HERKESE MUTLU SENELER!',
                ha='center', va='center', fontsize=52, fontweight='bold',
                color='#128C7E') 
        
        # Support CTA
        ax.text(0.5, 0.4, "Beğendiyseniz Github'da yıldız bırakarak\nveya paylaşarak destek olabilirsiniz ❤️",
                ha='center', va='center', fontsize=24,
                color='#7f8c8d', style='italic')
        
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        self._add_footer(fig)
        pdf.savefig(fig)
        plt.close()

def render_pdf(data: dict, user_map: dict = None) -> bytes:
    """
    Renders the analysis data into a PDF file in memory.
    """
    # Convert JS proxy to dict if needed (handled in main.py usually, but good to be safe)
    if hasattr(user_map, 'to_py'):
        user_map = user_map.to_py()
        
    renderer = RecapRenderer(data, user_map=user_map)
    return renderer.generate()
