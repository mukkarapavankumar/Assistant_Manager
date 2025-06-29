"""
Outlook COM Diagnostic Script
Test Outlook COM integration step by step to identify issues.
"""

import sys
import os
import traceback
from datetime import datetime

def test_pywin32_import():
    """Test if pywin32 is properly installed."""
    print("=" * 50)
    print("1. Testing pywin32 import...")
    try:
        import win32com.client
        import pythoncom
        print("✅ pywin32 successfully imported")
        return True
    except ImportError as e:
        print(f"❌ Failed to import pywin32: {e}")
        print("💡 Solution: pip install pywin32")
        return False
    except Exception as e:
        print(f"❌ Unexpected error importing pywin32: {e}")
        return False

def test_com_initialization():
    """Test COM initialization."""
    print("\n" + "=" * 50)
    print("2. Testing COM initialization...")
    try:
        import pythoncom
        pythoncom.CoInitialize()
        print("✅ COM initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize COM: {e}")
        return False

def test_outlook_application():
    """Test Outlook application creation."""
    print("\n" + "=" * 50)
    print("3. Testing Outlook application creation...")
    try:
        import win32com.client
        
        # Try to connect to existing Outlook instance first
        try:
            outlook = win32com.client.GetActiveObject("Outlook.Application")
            print("✅ Connected to existing Outlook instance")
        except:
            # If no active instance, try to create new one
            outlook = win32com.client.Dispatch("Outlook.Application")
            print("✅ Created new Outlook application instance")
        
        print(f"   Outlook version: {getattr(outlook, 'Version', 'Unknown')}")
        return outlook
    except Exception as e:
        print(f"❌ Failed to create Outlook application: {e}")
        print("💡 Possible solutions:")
        print("   - Make sure Outlook is installed")
        print("   - Try running Outlook manually first")
        print("   - Check if running as administrator is needed")
        return None

def test_outlook_namespace(outlook):
    """Test Outlook namespace access."""
    print("\n" + "=" * 50)
    print("4. Testing Outlook namespace access...")
    try:
        namespace = outlook.GetNamespace("MAPI")
        print("✅ Successfully accessed MAPI namespace")
        return namespace
    except Exception as e:
        print(f"❌ Failed to access namespace: {e}")
        print("💡 Possible solutions:")
        print("   - Outlook might not be properly configured")
        print("   - MAPI profile might be missing")
        return None

def test_default_folders(namespace):
    """Test access to default Outlook folders."""
    print("\n" + "=" * 50)
    print("5. Testing default folder access...")
    
    folders_to_test = [
        (6, "Inbox", "olFolderInbox"),
        (10, "Contacts", "olFolderContacts"),
        (5, "Sent Items", "olFolderSentMail"),
        (3, "Deleted Items", "olFolderDeletedItems")
    ]
    
    accessible_folders = []
    
    for folder_id, folder_name, folder_constant in folders_to_test:
        try:
            folder = namespace.GetDefaultFolder(folder_id)
            item_count = folder.Items.Count
            print(f"✅ {folder_name}: {item_count} items")
            accessible_folders.append(folder_name)
        except Exception as e:
            print(f"❌ {folder_name}: Failed to access - {e}")
    
    return accessible_folders

def test_contacts_search(namespace):
    """Test searching contacts specifically."""
    print("\n" + "=" * 50)
    print("6. Testing contacts search...")
    try:
        contacts_folder = namespace.GetDefaultFolder(10)  # olFolderContacts
        contact_items = contacts_folder.Items
        
        print(f"   Total contacts: {contact_items.Count}")
        
        # Try to iterate through a few contacts
        found_contacts = []
        for i, contact in enumerate(contact_items):
            if i >= 5:  # Limit to first 5 for testing
                break
            try:
                name = getattr(contact, 'FullName', '') or getattr(contact, 'CompanyName', 'Unknown')
                email = getattr(contact, 'Email1Address', 'No email')
                found_contacts.append({"name": name, "email": email})
                print(f"   Contact {i+1}: {name} ({email})")
            except Exception as e:
                print(f"   Contact {i+1}: Error reading - {e}")
        
        return found_contacts
        
    except Exception as e:
        print(f"❌ Failed to search contacts: {e}")
        return []

def test_address_book_access(namespace):
    """Test Global Address List access."""
    print("\n" + "=" * 50)
    print("7. Testing Global Address List (GAL) access...")
    try:
        address_lists = namespace.AddressLists
        print(f"   Found {address_lists.Count} address lists")
        
        for i, addr_list in enumerate(address_lists):
            list_name = addr_list.Name
            print(f"   Address List {i+1}: {list_name}")
            
            if "Global Address List" in list_name or "GAL" in list_name:
                try:
                    entries = addr_list.AddressEntries
                    print(f"     GAL entries: {entries.Count}")
                    
                    # Try to read first few entries
                    for j, entry in enumerate(entries):
                        if j >= 3:  # Limit to first 3
                            break
                        try:
                            name = entry.Name
                            print(f"     Entry {j+1}: {name}")
                        except Exception as e:
                            print(f"     Entry {j+1}: Error reading - {e}")
                            
                except Exception as e:
                    print(f"     Error accessing GAL entries: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to access address lists: {e}")
        return False

def test_simple_search(namespace, search_term="test"):
    """Test a simple contact search."""
    print("\n" + "=" * 50)
    print(f"8. Testing simple search for '{search_term}'...")
    
    found_contacts = []
    
    # Search in contacts
    try:
        contacts_folder = namespace.GetDefaultFolder(10)
        contact_items = contacts_folder.Items
        
        for contact in contact_items:
            try:
                name = getattr(contact, 'FullName', '') or getattr(contact, 'CompanyName', '')
                email = getattr(contact, 'Email1Address', '')
                
                if (search_term.lower() in name.lower() or 
                    search_term.lower() in email.lower()):
                    found_contacts.append({
                        'name': name,
                        'email': email,
                        'source': 'contacts'
                    })
                    
            except Exception as e:
                continue
        
        print(f"   Found {len(found_contacts)} matching contacts")
        for contact in found_contacts[:3]:  # Show first 3
            print(f"   - {contact['name']} ({contact['email']})")
            
    except Exception as e:
        print(f"❌ Error searching contacts: {e}")
    
    return found_contacts

def test_email_sending_capability(outlook):
    """Test if we can create (but not send) an email."""
    print("\n" + "=" * 50)
    print("9. Testing email creation capability...")
    try:
        mail = outlook.CreateItem(0)  # olMailItem
        mail.Subject = "Test Email (Not Sent)"
        mail.Body = "This is a test email created via COM."
        mail.To = "test@example.com"
        
        # Don't actually send, just test creation
        print("✅ Successfully created email item")
        print("   (Email was created but not sent)")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create email: {e}")
        return False

def run_comprehensive_test():
    """Run all tests and provide summary."""
    print("🔍 OUTLOOK COM DIAGNOSTIC SCRIPT")
    print("=" * 50)
    print(f"Started at: {datetime.now()}")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    
    results = {}
    outlook = None
    namespace = None
    
    # Run tests in sequence
    results['pywin32'] = test_pywin32_import()
    
    if results['pywin32']:
        results['com_init'] = test_com_initialization()
        
        if results['com_init']:
            outlook = test_outlook_application()
            results['outlook_app'] = outlook is not None
            
            if outlook:
                namespace = test_outlook_namespace(outlook)
                results['namespace'] = namespace is not None
                
                if namespace:
                    results['folders'] = test_default_folders(namespace)
                    results['contacts'] = test_contacts_search(namespace)
                    results['address_lists'] = test_address_book_access(namespace)
                    results['search'] = test_simple_search(namespace, "a")  # Search for 'a'
                    results['email_creation'] = test_email_sending_capability(outlook)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    issues_found = []
    
    if not results.get('pywin32'):
        issues_found.append("pywin32 not properly installed")
    if not results.get('com_init'):
        issues_found.append("COM initialization failed")
    if not results.get('outlook_app'):
        issues_found.append("Cannot create Outlook application")
    if not results.get('namespace'):
        issues_found.append("Cannot access MAPI namespace")
    if not results.get('folders'):
        issues_found.append("Cannot access default folders")
    
    if issues_found:
        print("❌ ISSUES FOUND:")
        for issue in issues_found:
            print(f"   - {issue}")
        
        print("\n💡 RECOMMENDED SOLUTIONS:")
        if not results.get('pywin32'):
            print("   1. Install pywin32: pip install pywin32")
        if not results.get('outlook_app'):
            print("   2. Ensure Outlook is installed and can run manually")
            print("   3. Try running this script as administrator")
            print("   4. Check for 32-bit vs 64-bit Python/Outlook compatibility")
        if not results.get('namespace'):
            print("   5. Set up Outlook with a valid email profile")
            print("   6. Run Outlook manually first to complete setup")
    else:
        print("✅ ALL TESTS PASSED!")
        print("   Outlook COM integration should work properly")
    
    # Cleanup
    try:
        if outlook:
            outlook = None
        import pythoncom
        pythoncom.CoUninitialize()
    except:
        pass
    
    return results

if __name__ == "__main__":
    try:
        results = run_comprehensive_test()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Unexpected error during testing: {e}")
        print("Traceback:")
        traceback.print_exc() 