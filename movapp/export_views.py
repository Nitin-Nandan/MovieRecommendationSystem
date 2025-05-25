import csv
import io
from datetime import datetime
from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from .data_loader import movie_data_loader
import json
import base64

def export_recommendations_csv(request):
    """Export recommendations as CSV file"""
    try:
        # Get recommendation data from request
        selected_movies = request.GET.getlist('selected_movies')
        filters = {}
        
        # Parse filters from request
        if request.GET.get('genres'):
            filters['genres'] = request.GET.getlist('genres')
        if request.GET.get('year_min'):
            filters['year_min'] = request.GET.get('year_min')
        if request.GET.get('year_max'):
            filters['year_max'] = request.GET.get('year_max')
        if request.GET.get('min_rating'):
            filters['min_rating'] = request.GET.get('min_rating')
        if request.GET.get('sort_by'):
            filters['sort_by'] = request.GET.get('sort_by')
        
        # Generate recommendations
        recommendations = movie_data_loader.get_filtered_recommendations(
            selected_movies, filters, 20
        )
        
        # Create CSV response
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"movie_recommendations_{timestamp}.csv"
        
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename="{filename}"'},
        )
        
        writer = csv.writer(response)
        
        # Write header
        writer.writerow([
            'Rank', 'Movie Title', 'Predicted Rating', 'Genres', 'Year', 'Genre Similarity'
        ])
        
        # Write recommendation data
        for i, movie in enumerate(recommendations, 1):
            year = movie.get('year', 'N/A')
            genres_str = ', '.join(movie.get('genres', []))
            genre_similarity = movie.get('genre_similarity', 'N/A')
            
            writer.writerow([
                i,
                movie['title'],
                movie['predicted_rating'],
                genres_str,
                year,
                genre_similarity
            ])
        
        return response
        
    except Exception as e:
        response = HttpResponse(f"Error generating CSV: {str(e)}", status=500)
        return response

def export_recommendations_pdf_fun(request):
    """Export recommendations as Fun Mode Star Wars-themed PDF"""
    return _export_pdf_internal(request, mode='fun')

def export_recommendations_pdf_pro(request):
    """Export recommendations as Pro Mode professional PDF"""
    return _export_pdf_internal(request, mode='pro')

def _export_pdf_internal(request, mode='pro'):
    """Internal PDF generation with dual modes"""
    try:
        # Get recommendation data from request
        selected_movies = request.GET.getlist('selected_movies')
        filters = {}
        
        # Parse filters from request
        if request.GET.get('genres'):
            filters['genres'] = request.GET.getlist('genres')
        if request.GET.get('year_min'):
            filters['year_min'] = request.GET.get('year_min')
        if request.GET.get('year_max'):
            filters['year_max'] = request.GET.get('year_max')
        if request.GET.get('min_rating'):
            filters['min_rating'] = request.GET.get('min_rating')
        if request.GET.get('sort_by'):
            filters['sort_by'] = request.GET.get('sort_by')
        
        # Generate recommendations
        recommendations = movie_data_loader.get_filtered_recommendations(
            selected_movies, filters, 20
        )
        
        # Create PDF buffer
        buffer = io.BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Get styles
        styles = getSampleStyleSheet()
        
        if mode == 'fun':
            # Fun Mode: Star Wars Theme
            story.extend(_create_fun_mode_content(styles, selected_movies, filters, recommendations))
            filename_prefix = "star_wars_movie_recommendations"
        else:
            # Pro Mode: Professional Cinema Theme
            story.extend(_create_pro_mode_content(styles, selected_movies, filters, recommendations))
            filename_prefix = "movie_recommendations_report"
        
        # Build PDF
        doc.build(story)
        
        # Return PDF response
        buffer.seek(0)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.pdf"
        
        return FileResponse(
            buffer, 
            as_attachment=True, 
            filename=filename,
            content_type='application/pdf'
        )
        
    except Exception as e:
        response = HttpResponse(f"Error generating PDF: {str(e)}", status=500)
        return response

def _create_fun_mode_content(styles, selected_movies, filters, recommendations):
    """Create Sith Empire-themed content for Fun Mode"""
    story = []
    
    # Dark Side Imperial styles
    imperial_title_style = ParagraphStyle(
        'ImperialTitle',
        parent=styles['Heading1'],
        fontSize=32,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=HexColor('#FF2E2E'),  # Sith red
        fontName='Helvetica-Bold'
    )
    
    sith_subtitle_style = ParagraphStyle(
        'SithSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=25,
        alignment=TA_CENTER,
        textColor=HexColor('#EEE'),  # Light gray
        fontName='Helvetica-Oblique'
    )
    
    imperial_section_style = ParagraphStyle(
        'ImperialSection',
        parent=styles['Heading3'],
        fontSize=16,
        spaceAfter=15,
        textColor=HexColor('#FF2E2E'),  # Sith red
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    )
    
    imperial_text_style = ParagraphStyle(
        'ImperialText',
        parent=styles['Normal'],
        fontSize=14,
        textColor=HexColor('#EEE'),
        leading=20,  # Line height 1.6
        spaceAfter=10
    )
    
    sith_quote_style = ParagraphStyle(
        'SithQuote',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER,
        textColor=HexColor('#FF2E2E'),
        fontName='Helvetica-Oblique',
        spaceAfter=15
    )
    
    imperial_footer_style = ParagraphStyle(
        'ImperialFooter',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=HexColor('#999'),
        spaceAfter=10
    )
    
    # Imperial bullet style
    imperial_bullet_style = ParagraphStyle(
        'ImperialBullet',
        parent=styles['Normal'],
        fontSize=12,
        leftIndent=20,
        textColor=HexColor('#EEE'),
        leading=18,
        bulletText='▶'
    )
    
    # Add Imperial header
    story.append(Paragraph("MOVIE RECOMMENDATIONS", imperial_title_style))
    story.append(Paragraph("IMPERIAL DATACORE TRANSMISSION", sith_subtitle_style))
    story.append(Paragraph("Classified intelligence for strategic entertainment deployment", imperial_text_style))
    story.append(Spacer(1, 20))
    
    # Add generation info
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    story.append(Paragraph(f"Transmission Date: {timestamp}", imperial_text_style))
    story.append(Paragraph("Authorization: Dark Lord of the Sith", sith_quote_style))
    story.append(Spacer(1, 25))
    
    # Imperial divider
    from reportlab.platypus import HRFlowable
    story.append(HRFlowable(width="100%", thickness=3, color=HexColor('#D90000')))
    story.append(Spacer(1, 15))
    
    # Add selected movies section - DARK SIDE LANGUAGE
    story.append(Paragraph("KNOWN REBEL-AFFILIATED CONTENT", imperial_section_style))
    story.append(Paragraph("Previously accessed entertainment assets:", imperial_text_style))
    for movie in selected_movies:
        story.append(Paragraph(f"▶ {movie}", imperial_bullet_style))
    story.append(Spacer(1, 20))
    
    # Add filters section - IMPERIAL PROTOCOL
    if filters:
        story.append(Paragraph("PROTOCOL APPLIED BY ORDER OF THE EMPEROR", imperial_section_style))
        story.append(Paragraph("Search parameters enforced by Imperial directive:", imperial_text_style))
        if filters.get('genres'):
            genres_str = ', '.join(filters['genres'])
            story.append(Paragraph(f"▶ Content Classification: {genres_str}", imperial_bullet_style))
        if filters.get('year_min') or filters.get('year_max'):
            year_range = f"{filters.get('year_min', '1900')}-{filters.get('year_max', '2024')}"
            story.append(Paragraph(f"▶ Production Cycles: {year_range}", imperial_bullet_style))
        if filters.get('min_rating'):
            story.append(Paragraph(f"▶ Minimum Force Index: {filters['min_rating']}+ units", imperial_bullet_style))
        if filters.get('sort_by'):
            story.append(Paragraph(f"▶ Sorting Protocol: {filters['sort_by']}", imperial_bullet_style))
        story.append(Spacer(1, 25))
    
    # Imperial divider
    story.append(HRFlowable(width="100%", thickness=3, color=HexColor('#D90000')))
    story.append(Spacer(1, 15))
    
    # Add recommendations section - IMPERIAL INTEL
    story.append(Paragraph("DECRYPTED INTEL: HIGH-VALUE CINEMATIC ASSETS", imperial_section_style))
    story.append(Paragraph("Priority targets for strategic consumption", sith_quote_style))
    story.append(Spacer(1, 15))
    
    # Create Imperial table
    story.extend(_create_imperial_recommendations_table(recommendations))
    
    # Add Sith Code ending
    story.append(Spacer(1, 40))
    story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#D90000')))
    story.append(Spacer(1, 15))
    story.append(Paragraph('"Peace is a lie, there is only passion." – Sith Code', sith_quote_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Transmission complete. Logged by Imperial DataCore.", imperial_footer_style))
    
    return story



def _create_pro_mode_content(styles, selected_movies, filters, recommendations):
    """Create professional cinema-themed content for Pro Mode"""
    story = []
    
    # Professional custom styles
    title_style = ParagraphStyle(
        'CinemaTitle',
        parent=styles['Heading1'],
        fontSize=26,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=HexColor('#2C3E50'),
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CinemaSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=25,
        alignment=TA_CENTER,
        textColor=HexColor('#34495E'),
        fontName='Helvetica-Oblique'
    )
    
    section_style = ParagraphStyle(
        'CinemaSection',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=15,
        textColor=HexColor('#2C3E50'),
        fontName='Helvetica-Bold'
    )
    
    tagline_style = ParagraphStyle(
        'CinemaTagline',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER,
        textColor=HexColor('#7F8C8D'),
        fontName='Helvetica-Oblique',
        spaceAfter=30
    )
    
    # Add professional title
    story.append(Paragraph("MOVIE RECOMMENDATION REPORT", title_style))
    story.append(Paragraph("Lights. Camera. Recommend.", tagline_style))
    story.append(Paragraph("Your personalized screening schedule", subtitle_style))
    story.append(Spacer(1, 20))
    
    # Add generation info
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    timestamp_style = ParagraphStyle(
    'TimestampStyle',
    parent=styles['Normal'],
    fontSize=11,
    alignment=TA_CENTER,  # This centers the text
    textColor=HexColor('#7F8C8D'),
    spaceAfter=10
    )
    story.append(Paragraph(f"Report Generated: {timestamp}", timestamp_style))
    story.append(Paragraph("Curated by advanced machine learning algorithms", tagline_style))
    story.append(Spacer(1, 25))
    
    # Add selected movies section
    story.append(Paragraph("YOUR CURATED COLLECTION", section_style))
    story.append(Paragraph("Movies selected for analysis:", styles['Normal']))
    for movie in selected_movies:
        story.append(Paragraph(f"• {movie}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Add filters section if any
    if filters:
        story.append(Paragraph("ADVANCED SEARCH CRITERIA", section_style))
        story.append(Paragraph("Applied filtering parameters:", styles['Normal']))
        if filters.get('genres'):
            genres_str = ', '.join(filters['genres'])
            story.append(Paragraph(f"• Genre Focus: {genres_str}", styles['Normal']))
        if filters.get('year_min') or filters.get('year_max'):
            year_range = f"{filters.get('year_min', '1900')}-{filters.get('year_max', '2024')}"
            story.append(Paragraph(f"• Release Period: {year_range}", styles['Normal']))
        if filters.get('min_rating'):
            story.append(Paragraph(f"• Minimum Rating: {filters['min_rating']}+ stars", styles['Normal']))
        if filters.get('sort_by'):
            story.append(Paragraph(f"• Sorting Method: {filters['sort_by']}", styles['Normal']))
        story.append(Spacer(1, 25))
    
    # Add recommendations section
    story.append(Paragraph("PERSONALIZED RECOMMENDATIONS", section_style))
    story.append(Paragraph("Your screening schedule is ready.", tagline_style))
    story.append(Spacer(1, 15))
    
    # Create professional table
    story.extend(_create_recommendations_table(recommendations, mode='pro'))
    
    # Add professional footer
    footer_style = ParagraphStyle(
        'CinemaFooter',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_CENTER,
        textColor=HexColor('#2C3E50'),
        fontName='Helvetica-Bold'
    )
    
    tagline_footer_style = ParagraphStyle(
        'CinemaTaglineFooter',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER,
        textColor=HexColor('#7F8C8D'),
        fontName='Helvetica-Oblique'
    )
    
    story.append(Spacer(1, 40))
    story.append(Paragraph("Movie Recommendation System", footer_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Powered by collaborative filtering and machine learning", tagline_footer_style))
    story.append(Paragraph("The show must go on.", tagline_footer_style))
    
    return story

def _create_recommendations_table(recommendations, mode='pro'):
    """Create recommendations table with enhanced Star Wars styling"""
    story = []
    
    # Create table data
    table_data = [['Rank', 'Movie Title', 'Force Rating', 'Genres', 'Year']]
    
    for i, movie in enumerate(recommendations, 1):
        year = movie.get('year', 'Unknown')
        genres_str = ', '.join(movie.get('genres', [])[:3])
        if len(movie.get('genres', [])) > 3:
            genres_str += '...'
        
        # Format rating based on mode
        rating = movie['predicted_rating']
        if mode == 'fun':
            if rating >= 4.5:
                rating_str = f"★★★★★ {rating}/5 (Jedi Master)"
            elif rating >= 4.0:
                rating_str = f"★★★★☆ {rating}/5 (Jedi Knight)"
            elif rating >= 3.5:
                rating_str = f"★★★☆☆ {rating}/5 (Padawan)"
            else:
                rating_str = f"★★☆☆☆ {rating}/5"
        else:
            rating_str = f"{rating}/5"
        
        table_data.append([
            f"#{i}",
            movie['title'][:45] + ('...' if len(movie['title']) > 45 else ''),
            rating_str,
            genres_str,
            str(year)
        ])
    
    # Create table with enhanced styling
    table = Table(table_data, colWidths=[0.6*inch, 3.0*inch, 1.5*inch, 1.8*inch, 0.7*inch])
    
    if mode == 'fun':
        # Your enhanced Star Wars theme
        table.setStyle(TableStyle([
            # Header with your navy blue background and gold text
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFD700')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            
            # Data styling with your suggested alternating colors
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [
                HexColor('#F9F9F9'),  # Your light gray
                HexColor('#EFEFEF')   # Your alternating gray
            ]),
            ('TEXTCOLOR', (0, 1), (-1, -1), HexColor('#003366')),  # Navy text
            
            # Enhanced padding as you suggested
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            
            # Grid styling with gold borders
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#FFD700')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Center alignment for specific columns
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Rank
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),  # Rating
            ('ALIGN', (4, 0), (4, -1), 'CENTER'),  # Year
        ]))
    else:
        # Keep professional theme unchanged
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2C3E50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#FFFFFF'), HexColor('#F8F9FA')]),
            ('TEXTCOLOR', (0, 1), (-1, -1), HexColor('#2C3E50')),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#BDC3C7')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('ALIGN', (4, 0), (4, -1), 'CENTER'),
        ]))
    
    story.append(table)
    return story


def _create_imperial_recommendations_table(recommendations):
    """Create Imperial-themed recommendations table"""
    story = []
    
    # Create table data with Imperial terminology
    table_data = [['Rank', 'Subject', 'Force Index', 'Classification', 'Cycle']]
    
    for i, movie in enumerate(recommendations, 1):
        year = movie.get('year', 'Unknown')
        genres_str = ', '.join(movie.get('genres', [])[:3])
        if len(movie.get('genres', [])) > 3:
            genres_str += '...'
        
        # Imperial ranking system
        rating = movie['predicted_rating']
        if rating >= 4.5:
            rank_label = "Sith Lord"
            stars = "★★★★★"
        elif rating >= 4.0:
            rank_label = "Dark Acolyte"
            stars = "★★★★☆"
        elif rating >= 3.5:
            rank_label = "Imperial Agent"
            stars = "★★★☆☆"
        else:
            rank_label = "Stormtrooper"
            stars = "★★☆☆☆"
        
        force_index = f"{stars} {rating}/5 ({rank_label})"
        
        table_data.append([
            f"#{i}",
            movie['title'][:40] + ('...' if len(movie['title']) > 40 else ''),
            force_index,
            genres_str,
            str(year)
        ])
    
    # Create Imperial table with dark theme
    table = Table(table_data, colWidths=[0.6*inch, 2.8*inch, 1.7*inch, 1.8*inch, 0.7*inch])
    
    # Imperial styling - Dark Side theme
    table.setStyle(TableStyle([
        # Header with Imperial colors
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#660000')),  # Dark red
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFF')),      # White text
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        
        # Data styling with alternating dark rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [
            HexColor('#1a1a1a'),  # Very dark gray
            HexColor('#2a2a2a')   # Slightly lighter dark gray
        ]),
        ('TEXTCOLOR', (0, 1), (-1, -1), HexColor('#EEE')),  # Light gray text
        
        # Enhanced padding
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        
        # Imperial red borders
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#FF2E2E')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Center alignment for specific columns
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Rank
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),  # Force Index
        ('ALIGN', (4, 0), (4, -1), 'CENTER'),  # Cycle
    ]))
    
    story.append(table)
    return story


