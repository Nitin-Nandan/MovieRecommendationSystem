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
            # Extract year from title
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
        # Return error response
        response = HttpResponse(f"Error generating CSV: {str(e)}", status=500)
        return response

def export_recommendations_pdf(request):
    """Export recommendations as Star Wars-themed PDF file"""
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
        
        # Create PDF document with Star Wars theme
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Create Star Wars-themed custom styles
        title_style = ParagraphStyle(
            'StarWarsTitle',
            parent=styles['Heading1'],
            fontSize=28,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=HexColor('#FFD700'),  # Gold like Star Wars logo
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'StarWarsSubtitle',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=25,
            alignment=TA_CENTER,
            textColor=HexColor('#4169E1'),  # Royal blue
            fontName='Helvetica-Oblique'
        )
        
        section_style = ParagraphStyle(
            'SithSection',
            parent=styles['Heading3'],
            fontSize=16,
            spaceAfter=15,
            textColor=HexColor('#DC143C'),  # Sith red
            fontName='Helvetica-Bold'
        )
        
        jedi_style = ParagraphStyle(
            'JediSection',
            parent=styles['Heading3'],
            fontSize=16,
            spaceAfter=15,
            textColor=HexColor('#0066CC'),  # Jedi blue
            fontName='Helvetica-Bold'
        )
        
        # Star Wars opening crawl style
        crawl_style = ParagraphStyle(
            'OpeningCrawl',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            textColor=HexColor('#FFD700'),
            fontName='Helvetica-Oblique',
            spaceAfter=30
        )
        
        # Add Star Wars-themed title
        story.append(Paragraph("⭐ MOVIE RECOMMENDATIONS ⭐", title_style))
        story.append(Paragraph("🎬 A long time ago in a galaxy far, far away... 🎬", crawl_style))
        story.append(Paragraph("Your personalized movie journey begins", subtitle_style))
        story.append(Spacer(1, 20))
        
        # Add generation info with Star Wars flair
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        story.append(Paragraph(f"⚡ Generated on: {timestamp} ⚡", styles['Normal']))
        story.append(Paragraph("🌟 May the Force guide your movie choices! 🌟", crawl_style))
        story.append(Spacer(1, 25))
        
        # Add selected movies section (Jedi style)
        story.append(Paragraph("⚔️ JEDI COUNCIL SELECTIONS", jedi_style))
        story.append(Paragraph("Movies chosen by the Force within you:", styles['Normal']))
        for movie in selected_movies:
            story.append(Paragraph(f"🎭 {movie}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Add filters section if any (Sith style)
        if filters:
            story.append(Paragraph("🔥 SITH FILTERS APPLIED", section_style))
            story.append(Paragraph("Your path to the dark side of cinema:", styles['Normal']))
            if filters.get('genres'):
                genres_str = ', '.join(filters['genres'])
                story.append(Paragraph(f"⚡ Genres: {genres_str}", styles['Normal']))
            if filters.get('year_min') or filters.get('year_max'):
                year_range = f"{filters.get('year_min', '1900')}-{filters.get('year_max', '2024')}"
                story.append(Paragraph(f"📅 Galactic Years: {year_range}", styles['Normal']))
            if filters.get('min_rating'):
                story.append(Paragraph(f"⭐ Minimum Force Rating: {filters['min_rating']}+ stars", styles['Normal']))
            if filters.get('sort_by'):
                story.append(Paragraph(f"🔄 Sorted by the will of the Force: {filters['sort_by']}", styles['Normal']))
            story.append(Spacer(1, 25))
        
        # Add recommendations section
        story.append(Paragraph("✨ THE FORCE AWAKENS YOUR RECOMMENDATIONS", jedi_style))
        story.append(Paragraph("These are the movies you're looking for...", crawl_style))
        story.append(Spacer(1, 15))
        
        # Create Star Wars-themed recommendations table
        table_data = [['Rank', 'Movie Title', 'Force Rating', 'Galaxy Genres', 'Year']]
        
        for i, movie in enumerate(recommendations, 1):
            year = movie.get('year', 'Unknown')
            genres_str = ', '.join(movie.get('genres', [])[:3])
            if len(movie.get('genres', [])) > 3:
                genres_str += '...'
            
            # Add Star Wars flair to ratings
            rating = movie['predicted_rating']
            force_rating = f"⭐ {rating}/5"
            if rating >= 4.5:
                force_rating = f"🌟 {rating}/5 (Jedi Master)"
            elif rating >= 4.0:
                force_rating = f"⚔️ {rating}/5 (Jedi Knight)"
            elif rating >= 3.5:
                force_rating = f"⚡ {rating}/5 (Padawan)"
            
            table_data.append([
                f"#{i}",
                movie['title'][:45] + ('...' if len(movie['title']) > 45 else ''),
                force_rating,
                genres_str,
                str(year)
            ])
        
        # Create Star Wars-themed table
        table = Table(table_data, colWidths=[0.6*inch, 3.2*inch, 1.3*inch, 1.8*inch, 0.7*inch])
        table.setStyle(TableStyle([
            # Header styling (Death Star colors)
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2F2F2F')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFD700')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            
            # Data styling (alternating light/dark side)
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [
                HexColor('#F0F8FF'),  # Light side (Alice Blue)
                HexColor('#1C1C1C')   # Dark side
            ]),
            ('TEXTCOLOR', (0, 1), (-1, -1), HexColor('#000000')),
            
            # Dark side rows get light text
            *[('TEXTCOLOR', (0, i), (-1, i), HexColor('#FFD700')) 
              for i in range(2, len(table_data), 2)],
            
            # Grid styling
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#FFD700')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Center alignment for specific columns
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Rank
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),  # Rating
            ('ALIGN', (4, 0), (4, -1), 'CENTER'),  # Year
        ]))
        
        story.append(table)
        story.append(Spacer(1, 40))
        
        # Add Star Wars footer
        footer_style = ParagraphStyle(
            'StarWarsFooter',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            textColor=HexColor('#FFD700'),
            fontName='Helvetica-Bold'
        )
        
        quote_style = ParagraphStyle(
            'StarWarsQuote',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=HexColor('#4169E1'),
            fontName='Helvetica-Oblique'
        )
        
        story.append(Paragraph("🌌 Generated by the Movie Recommendation System 🌌", footer_style))
        story.append(Spacer(1, 10))
        story.append(Paragraph("⚔️ May the Force be with your movie choices! ⚡", quote_style))
        story.append(Paragraph("🎬 Remember: Do or do not watch... there is no try! 🎬", quote_style))
        
        # Build PDF
        doc.build(story)
        
        # Return PDF response
        buffer.seek(0)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"star_wars_movie_recommendations_{timestamp}.pdf"
        
        return FileResponse(
            buffer, 
            as_attachment=True, 
            filename=filename,
            content_type='application/pdf'
        )
        
    except Exception as e:
        response = HttpResponse(f"Error generating Star Wars PDF: {str(e)}", status=500)
        return response

