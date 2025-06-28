"""
Script to generate sample HR policy PDF documents.

This script demonstrates how to use the generic PDFGenerator utility
to create specific HR policy documents. It shows the separation between
generic utilities and specific use cases.
"""
from .pdf_generator import PDFGenerator

# Sample HR policy documents
samples = [
    ("hr_policy_generic.pdf", "Company HR Policy\n==================\n\n1. Vacation Policy: All employees are entitled to 20 days of paid vacation per year.\n2. Sick Leave: Employees may take up to 10 days of paid sick leave annually.\n3. Remote Work: Employees may work remotely up to 2 days per week with manager approval.\n4. Benefits: Health insurance and retirement plans are provided to all full-time employees.\n5. Code of Conduct: All employees must adhere to the company's code of conduct and ethics guidelines."),
    ("hr_policy_engineering.pdf", "Engineering Department HR Policy\n==============================\n\n1. Vacation Policy: Engineering staff are entitled to 25 days of paid vacation per year.\n2. On-call Rotation: Engineers participate in an on-call rotation and receive additional compensation.\n3. Training: Engineers are eligible for up to $2,000 per year in professional development reimbursement.\n4. Remote Work: Engineering staff may work remotely up to 3 days per week.\n5. Equipment: The company provides high-performance laptops and monitors for all engineers."),
    ("hr_policy_sales.pdf", "Sales Department HR Policy\n=========================\n\n1. Vacation Policy: Sales staff are entitled to 20 days of paid vacation per year.\n2. Commission: Sales employees receive commission based on quarterly targets.\n3. Travel: Sales staff may be required to travel up to 30% of the time; expenses are reimbursed.\n4. Training: Sales team members receive quarterly training on products and sales techniques.\n5. Remote Work: Sales staff may work remotely up to 1 day per week.")
]

def main():
    """Generate sample HR policy PDF documents using the generic PDFGenerator utility."""
    # Initialize the generic PDF generator
    pdf_generator = PDFGenerator(output_dir="data")
    
    # Use the generic utility to create multiple PDFs
    created_files = pdf_generator.create_multiple_pdfs(samples)
    
    print(f"Created {len(created_files)} HR policy PDF files:")
    for filepath in created_files:
        print(f"  - {filepath}")

if __name__ == "__main__":
    main() 