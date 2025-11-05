import requests
import json
import time
import sys

# Configuration
SEARCHAPI_URL = "https://www.searchapi.io/api/v1/search"

# Dork list
DORKS = [
    "site:{target} ext:doc | ext:docx | ext:odt | ext:rtf | ext:sxw | ext:psw | ext:ppt | ext:pptx | ext:pps | ext:csv",
    "site:{target} intitle:index.of",
    "site:{target} ext:xml | ext:conf | ext:cnf | ext:reg | ext:inf | ext:rdp | ext:cfg | ext:txt | ext:ora | ext:ini | ext:env",
    "site:{target} ext:sql | ext:dbf | ext:mdb",
    "site:{target} ext:log",
    "site:{target} ext:bkf | ext:bkp | ext:bak | ext:old | ext:backup",
    "site:{target} inurl:login | inurl:signin | intitle:Login | intitle:\"sign in\" | inurl:auth",
    "site:{target} intext:\"sql syntax near\" | intext:\"syntax error has occurred\" | intext:\"incorrect syntax near\" | intext:\"unexpected end of SQL command\" | intext:\"Warning: mysql_connect()\" | intext:\"Warning: mysql_query()\" | intext:\"Warning: pg_connect()\"",
    "site:{target} \"PHP Parse error\" | \"PHP Warning\" | \"PHP Error\"",
    "site:{target} ext:php intitle:phpinfo \"published by the PHP Group\"",
    "site:pastebin.com | site:paste2.org | site:pastehtml.com | site:slexy.org | site:snipplr.com | site:snipt.net | site:textsnip.com | site:bitpaste.app | site:justpaste.it | site:heypasteit.com | site:hastebin.com | site:dpaste.org | site:dpaste.com | site:codepad.org | site:jsitor.com | site:codepen.io | site:jsfiddle.net | site:dotnetfiddle.net | site:phpfiddle.org | site:ide.geeksforgeeks.org | site:repl.it | site:ideone.com | site:paste.debian.net | site:paste.org | site:paste.org.ru | site:codebeautify.org | site:codeshare.io | site:trello.com \"{target}\"",
    "site:github.com | site:gitlab.com \"{target}\"",
    "site:stackoverflow.com \"{target}\"",
    "site:{target} inurl:signup | inurl:register | intitle:Signup",
    "site:*.{target}",
    "site:*.*.{target}",
    "https://web.archive.org/web/*/{target}/*",
    "({target}) (site:*.*.29.* |site:*.*.28.* |site:*.*.27.* |site:*.*.26.* |site:*.*.25.* |site:*.*.24.* |site:*.*.23.* |site:*.*.22.* |site:*.*.21.* |site:*.*.20.* |site:*.*.19.* |site:*.*.18.* |site:*.*.17.* |site:*.*.16.* |site:*.*.15.* |site:*.*.14.* |site:*.*.13.* |site:*.*.12.* |site:*.*.11.* |site:*.*.10.* |site:*.*.9.* |site:*.*.8.* |site:*.*.7.* |site:*.*.6.* |site:*.*.5.* |site:*.*.4.* |site:*.*.3.* |site:*.*.2.* |site:*.*.1.* |site:*.*.0.*)"
]

class SearchAPIManager:
    def __init__(self, api_keys):
        self.api_keys = api_keys
        self.current_key_index = 0
        self.total_requests = 0
        self.failed_requests = 0
        
    def get_current_key(self):
        """Get currently active API key"""
        if not self.api_keys:
            return None
        return self.api_keys[self.current_key_index]
    
    def rotate_key(self):
        """Rotate to next API key"""
        if len(self.api_keys) <= 1:
            return False  # No other keys to rotate to
        
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        print(f"🔄 Rotating to API key {self.current_key_index + 1}/{len(self.api_keys)}")
        return True
    
    def search_dork(self, dork_query):
        """Perform search using SearchAPI.io with fallback mechanism"""
        if not self.api_keys:
            print("❌ No API keys available!")
            return None
            
        current_key = self.get_current_key()
        
        try:
            params = {
                "engine": "google",
                "q": dork_query,
                "api_key": current_key
            }
            
            self.total_requests += 1
            response = requests.get(SEARCHAPI_URL, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            self.failed_requests += 1
            if response.status_code == 429:  # Rate limit
                print(f"⚠️  API key {self.current_key_index + 1} rate limited")
                if self.rotate_key():
                    return self.search_dork(dork_query)  # Retry with new key
                else:
                    print("❌ All API keys rate limited")
                    return None
            else:
                print(f"❌ HTTP Error with API key {self.current_key_index + 1}: {e}")
                if self.rotate_key():
                    return self.search_dork(dork_query)
                else:
                    return None
                    
        except requests.exceptions.RequestException as e:
            self.failed_requests += 1
            print(f"❌ Request error with API key {self.current_key_index + 1}: {e}")
            if self.rotate_key():
                return self.search_dork(dork_query)
            else:
                return None
        except json.JSONDecodeError as e:
            self.failed_requests += 1
            print(f"❌ JSON parsing error: {e}")
            return None
    
    def get_stats(self):
        """Get API usage statistics"""
        return {
            'total_requests': self.total_requests,
            'failed_requests': self.failed_requests,
            'success_rate': ((self.total_requests - self.failed_requests) / self.total_requests * 100) if self.total_requests > 0 else 0,
            'current_key': self.current_key_index + 1,
            'total_keys': len(self.api_keys)
        }

def main():
    print("=== Google Dork Reconnaissance Tool by Hades ===")
    print("Automated surface-level security assessment using search engine queries\n")
    
    # Input multiple API keys
    api_keys_input = input("Enter API keys (comma-separated): ").strip()
    
    if not api_keys_input:
        print("❌ Error: At least one API key is required!")
        return
    
    api_keys = [key.strip() for key in api_keys_input.split(',') if key.strip()]
    
    if not api_keys:
        print("❌ Error: No valid API keys found!")
        return
    
    print(f"✅ Loaded {len(api_keys)} API key(s)")
    
    # Input target domain
    target = input("Enter target domain (example: example.com): ").strip()
    
    if not target:
        print("❌ Error: Target domain cannot be empty!")
        return
    
    # Initialize API manager
    api_manager = SearchAPIManager(api_keys)
    
    print(f"\nStarting reconnaissance for: {target}")
    print("=" * 60)
    
    found_results = False
    successful_dorks = 0
    
    for i, dork_template in enumerate(DORKS, 1):
        # Replace placeholder with target domain
        dork_query = dork_template.format(target=target)
        
        print(f"\n[{i}/{len(DORKS)}] Testing dork: {dork_query}")
        
        # Perform search
        results = api_manager.search_dork(dork_query)
        
        # Brief delay to avoid rate limiting
        time.sleep(1)
        
        if results and 'organic_results' in results and results['organic_results']:
            found_results = True
            successful_dorks += 1
            print(f"✅ FOUND {len(results['organic_results'])} results:")
            
            for j, result in enumerate(results['organic_results'], 1):
                title = result.get('title', 'No title')
                link = result.get('link', 'No link')
                snippet = result.get('snippet', 'No snippet')[:100] + "..." if result.get('snippet') else 'No snippet'
                print(f"   {j}. {title}")
                print(f"      📍 {link}")
                print(f"      📝 {snippet}")
                print()
        else:
            print("   ❌ No results found")
        
        # Display interim statistics
        stats = api_manager.get_stats()
        if i % 5 == 0:  # Display statistics every 5 dorks
            print(f"\n📊 Statistics: {stats['total_requests']} requests, "
                  f"{stats['failed_requests']} failed, "
                  f"Success rate: {stats['success_rate']:.1f}%")
        
        print("-" * 80)
    
    # Display final summary
    print("\n" + "=" * 60)
    print("📋 SCANNING SUMMARY")
    print("=" * 60)
    print(f"Target: {target}")
    print(f"Total dorks tested: {len(DORKS)}")
    print(f"Dorks with results: {successful_dorks}")
    
    stats = api_manager.get_stats()
    print(f"\n📊 API STATISTICS:")
    print(f"Total API keys: {stats['total_keys']}")
    print(f"Total requests: {stats['total_requests']}")
    print(f"Failed requests: {stats['failed_requests']}")
    print(f"Success rate: {stats['success_rate']:.1f}%")
    print(f"Last used API key: #{stats['current_key']}")
    
    if not found_results:
        print("\n❌ No results found for any tested dorks.")
    else:
        print(f"\n✅ Reconnaissance complete! Found results for {successful_dorks} dorks.")

if __name__ == "__main__":
    main()
