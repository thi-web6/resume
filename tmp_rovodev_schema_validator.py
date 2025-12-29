#!/usr/bin/env python3
"""
Schema.org Structured Data Validator
Validates against official Schema.org documentation and Google's structured data guidelines
"""

import json
import re
from typing import List, Dict, Tuple

def extract_json_ld(html_content: str) -> List[Dict]:
    """Extract all JSON-LD blocks from HTML"""
    scripts = re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', html_content, re.DOTALL)
    json_blocks = []
    for i, script in enumerate(scripts, 1):
        try:
            data = json.loads(script)
            json_blocks.append({"index": i, "type": data.get("@type", "Unknown"), "data": data})
        except json.JSONDecodeError as e:
            json_blocks.append({"index": i, "type": "INVALID", "error": str(e)})
    return json_blocks

def validate_person_schema(data: Dict) -> List[str]:
    """Validate Person schema against Schema.org specification"""
    issues = []
    warnings = []
    
    # Required properties for Person (Google recommendation)
    required = ["@type", "name"]
    recommended = ["image", "jobTitle", "url"]
    
    for prop in required:
        if prop not in data:
            issues.append(f"❌ CRITICAL: Missing required property '{prop}'")
    
    for prop in recommended:
        if prop not in data:
            warnings.append(f"⚠️  WARNING: Missing recommended property '{prop}'")
    
    # Check for duplicate properties
    json_str = json.dumps(data)
    properties = ["nationality", "name", "email", "telephone", "birthDate", "gender", "url"]
    for prop in properties:
        matches = re.findall(f'"{prop}":', json_str)
        if len(matches) > 1:
            issues.append(f"❌ CRITICAL: Duplicate property '{prop}' found {len(matches)} times")
    
    # Validate data types
    if "birthDate" in data:
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', str(data["birthDate"])):
            issues.append(f"❌ CRITICAL: 'birthDate' must be in ISO 8601 format (YYYY-MM-DD)")
    
    if "email" in data:
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', str(data["email"])):
            issues.append(f"❌ CRITICAL: 'email' format is invalid")
    
    if "image" in data:
        if isinstance(data["image"], dict):
            if "@type" not in data["image"] or data["image"]["@type"] != "ImageObject":
                warnings.append(f"⚠️  WARNING: 'image' should have @type: ImageObject")
            if "url" not in data["image"]:
                issues.append(f"❌ CRITICAL: 'image' object missing 'url' property")
        elif not isinstance(data["image"], str):
            issues.append(f"❌ CRITICAL: 'image' must be string URL or ImageObject")
    
    # Validate nested objects
    if "address" in data:
        if not isinstance(data["address"], dict):
            issues.append(f"❌ CRITICAL: 'address' must be an object")
        elif "@type" not in data["address"]:
            issues.append(f"❌ CRITICAL: 'address' missing @type property")
    
    if "alumniOf" in data:
        if isinstance(data["alumniOf"], dict):
            if "@type" not in data["alumniOf"]:
                issues.append(f"❌ CRITICAL: 'alumniOf' missing @type property")
    
    # Check hasOccupation structure
    if "hasOccupation" in data:
        occ = data["hasOccupation"]
        if not isinstance(occ, dict):
            issues.append(f"❌ CRITICAL: 'hasOccupation' must be an object")
        elif "@type" not in occ or occ["@type"] != "Occupation":
            issues.append(f"❌ CRITICAL: 'hasOccupation' must have @type: Occupation")
    
    # Validate award array
    if "award" in data:
        if not isinstance(data["award"], list):
            issues.append(f"❌ CRITICAL: 'award' must be an array")
        else:
            for i, award in enumerate(data["award"]):
                if not isinstance(award, dict):
                    issues.append(f"❌ CRITICAL: award[{i}] must be an object")
                elif "@type" not in award:
                    warnings.append(f"⚠️  WARNING: award[{i}] missing @type property")
                elif "name" not in award:
                    issues.append(f"❌ CRITICAL: award[{i}] missing 'name' property")
    
    # Validate memberOf array
    if "memberOf" in data:
        if not isinstance(data["memberOf"], list):
            issues.append(f"❌ CRITICAL: 'memberOf' must be an array")
        else:
            for i, org in enumerate(data["memberOf"]):
                if not isinstance(org, dict):
                    issues.append(f"❌ CRITICAL: memberOf[{i}] must be an object")
                elif "@type" not in org:
                    warnings.append(f"⚠️  WARNING: memberOf[{i}] missing @type property")
    
    return issues, warnings

def validate_organization_schema(data: Dict) -> Tuple[List[str], List[str]]:
    """Validate Organization schema"""
    issues = []
    warnings = []
    
    if "name" not in data:
        issues.append(f"❌ CRITICAL: Missing required property 'name'")
    
    if "url" not in data:
        warnings.append(f"⚠️  WARNING: Missing recommended property 'url'")
    
    if "address" in data:
        if not isinstance(data["address"], dict):
            issues.append(f"❌ CRITICAL: 'address' must be an object")
        elif "@type" not in data["address"]:
            issues.append(f"❌ CRITICAL: 'address' missing @type property")
    
    return issues, warnings

def validate_website_schema(data: Dict) -> Tuple[List[str], List[str]]:
    """Validate WebSite schema"""
    issues = []
    warnings = []
    
    if "url" not in data:
        issues.append(f"❌ CRITICAL: Missing required property 'url'")
    
    if "name" not in data:
        warnings.append(f"⚠️  WARNING: Missing recommended property 'name'")
    
    if "potentialAction" in data:
        action = data["potentialAction"]
        if not isinstance(action, dict):
            issues.append(f"❌ CRITICAL: 'potentialAction' must be an object")
        elif "@type" not in action:
            issues.append(f"❌ CRITICAL: 'potentialAction' missing @type property")
    
    return issues, warnings

def validate_article_schema(data: Dict) -> Tuple[List[str], List[str]]:
    """Validate Article schema"""
    issues = []
    warnings = []
    
    required = ["headline", "author", "datePublished"]
    for prop in required:
        if prop not in data:
            issues.append(f"❌ CRITICAL: Missing required property '{prop}'")
    
    if "author" in data:
        if isinstance(data["author"], dict):
            if "@type" not in data["author"]:
                issues.append(f"❌ CRITICAL: 'author' missing @type property")
    
    if "publisher" in data:
        if isinstance(data["publisher"], dict):
            if "@type" not in data["publisher"]:
                issues.append(f"❌ CRITICAL: 'publisher' missing @type property")
            if "logo" in data["publisher"]:
                logo = data["publisher"]["logo"]
                if isinstance(logo, dict) and "@type" not in logo:
                    warnings.append(f"⚠️  WARNING: publisher.logo missing @type property")
    
    return issues, warnings

def validate_breadcrumb_schema(data: Dict) -> Tuple[List[str], List[str]]:
    """Validate BreadcrumbList schema"""
    issues = []
    warnings = []
    
    if "itemListElement" not in data:
        issues.append(f"❌ CRITICAL: Missing required property 'itemListElement'")
    else:
        items = data["itemListElement"]
        if not isinstance(items, list):
            issues.append(f"❌ CRITICAL: 'itemListElement' must be an array")
        else:
            for i, item in enumerate(items):
                if not isinstance(item, dict):
                    issues.append(f"❌ CRITICAL: itemListElement[{i}] must be an object")
                else:
                    if "@type" not in item or item["@type"] != "ListItem":
                        issues.append(f"❌ CRITICAL: itemListElement[{i}] must have @type: ListItem")
                    if "position" not in item:
                        issues.append(f"❌ CRITICAL: itemListElement[{i}] missing 'position'")
                    if "name" not in item:
                        issues.append(f"❌ CRITICAL: itemListElement[{i}] missing 'name'")
    
    return issues, warnings

def validate_faq_schema(data: Dict) -> Tuple[List[str], List[str]]:
    """Validate FAQPage schema"""
    issues = []
    warnings = []
    
    if "mainEntity" not in data:
        issues.append(f"❌ CRITICAL: Missing required property 'mainEntity'")
    else:
        entities = data["mainEntity"]
        if not isinstance(entities, list):
            issues.append(f"❌ CRITICAL: 'mainEntity' must be an array")
        else:
            for i, entity in enumerate(entities):
                if not isinstance(entity, dict):
                    issues.append(f"❌ CRITICAL: mainEntity[{i}] must be an object")
                else:
                    if "@type" not in entity or entity["@type"] != "Question":
                        issues.append(f"❌ CRITICAL: mainEntity[{i}] must have @type: Question")
                    if "name" not in entity:
                        issues.append(f"❌ CRITICAL: mainEntity[{i}] missing 'name' (question text)")
                    if "acceptedAnswer" not in entity:
                        issues.append(f"❌ CRITICAL: mainEntity[{i}] missing 'acceptedAnswer'")
                    elif isinstance(entity["acceptedAnswer"], dict):
                        answer = entity["acceptedAnswer"]
                        if "@type" not in answer or answer["@type"] != "Answer":
                            issues.append(f"❌ CRITICAL: mainEntity[{i}].acceptedAnswer must have @type: Answer")
                        if "text" not in answer:
                            issues.append(f"❌ CRITICAL: mainEntity[{i}].acceptedAnswer missing 'text'")
    
    return issues, warnings

def main():
    print("=" * 80)
    print("Schema.org Structured Data Validator")
    print("Validating against official Schema.org & Google guidelines")
    print("=" * 80)
    print()
    
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    json_blocks = extract_json_ld(content)
    
    print(f"📊 Found {len(json_blocks)} JSON-LD blocks\n")
    
    total_issues = 0
    total_warnings = 0
    
    for block in json_blocks:
        index = block["index"]
        schema_type = block["type"]
        
        print(f"\n{'='*80}")
        print(f"Block #{index}: {schema_type}")
        print(f"{'='*80}")
        
        if schema_type == "INVALID":
            print(f"❌ CRITICAL: Invalid JSON - {block['error']}")
            total_issues += 1
            continue
        
        data = block["data"]
        issues = []
        warnings = []
        
        # Validate based on type
        if schema_type == "Person":
            issues, warnings = validate_person_schema(data)
        elif schema_type in ["Organization", "EducationalOrganization"]:
            issues, warnings = validate_organization_schema(data)
        elif schema_type == "WebSite":
            issues, warnings = validate_website_schema(data)
        elif schema_type == "Article":
            issues, warnings = validate_article_schema(data)
        elif schema_type == "BreadcrumbList":
            issues, warnings = validate_breadcrumb_schema(data)
        elif schema_type == "FAQPage":
            issues, warnings = validate_faq_schema(data)
        
        # Print results
        if not issues and not warnings:
            print("✅ PASSED: All validations passed!")
        else:
            if issues:
                print(f"\n🔴 CRITICAL ISSUES ({len(issues)}):")
                for issue in issues:
                    print(f"  {issue}")
                total_issues += len(issues)
            
            if warnings:
                print(f"\n🟡 WARNINGS ({len(warnings)}):")
                for warning in warnings:
                    print(f"  {warning}")
                total_warnings += len(warnings)
    
    # Summary
    print(f"\n{'='*80}")
    print(f"VALIDATION SUMMARY")
    print(f"{'='*80}")
    print(f"Total JSON-LD Blocks: {len(json_blocks)}")
    print(f"Critical Issues: {total_issues}")
    print(f"Warnings: {total_warnings}")
    
    if total_issues == 0 and total_warnings == 0:
        print("\n🎉 ALL STRUCTURED DATA IS VALID!")
        print("✅ Ready for Google Search Console testing")
    elif total_issues == 0:
        print(f"\n✅ No critical issues found")
        print(f"⚠️  {total_warnings} warnings - consider fixing for optimal SEO")
    else:
        print(f"\n❌ {total_issues} critical issues found - MUST be fixed!")
        print("Google Search Console will show errors for these issues")
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    main()
