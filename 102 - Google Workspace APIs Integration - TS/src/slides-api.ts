/**
 * Google Slides API Functions - Implementation from document lines 2284-2698
 *
 * This module implements all Slides API functions from Section 5 of the guide.
 */
import { slides_v1 } from 'googleapis';
import { v4 as uuidv4 } from 'uuid';

// ==================== CREATE PRESENTATIONS (Section 5.1) ====================

/**
 * Create a new Google Slides presentation.
 *
 * @param slidesService - Slides API service instance
 * @param title - Presentation title
 * @returns Created presentation metadata
 */
export async function createPresentation(
  slidesService: slides_v1.Slides,
  title: string
): Promise<slides_v1.Schema$Presentation> {
  const presentation: slides_v1.Schema$Presentation = {
    title,
  };

  const response = await slidesService.presentations.create({
    requestBody: presentation,
  });

  return response.data;
}

/**
 * Create a presentation with multiple blank slides.
 *
 * @param slidesService - Slides API service instance
 * @param title - Presentation title
 * @param slideCount - Number of slides to create
 * @returns Created presentation
 */
export async function createPresentationWithSlides(
  slidesService: slides_v1.Slides,
  title: string,
  slideCount: number = 5
): Promise<slides_v1.Schema$Presentation> {
  const presentation = await createPresentation(slidesService, title);
  const presentationId = presentation.presentationId!;

  // Add additional slides (first slide is created automatically)
  const requests: slides_v1.Schema$Request[] = [];
  for (let i = 0; i < slideCount - 1; i++) {
    requests.push({
      createSlide: {
        insertionIndex: i + 1,
        slideLayoutReference: {
          predefinedLayout: 'BLANK',
        },
      },
    });
  }

  if (requests.length > 0) {
    await slidesService.presentations.batchUpdate({
      presentationId,
      requestBody: { requests },
    });
  }

  return presentation;
}

// ==================== READ PRESENTATIONS (Section 5.2) ====================

/**
 * Get presentation metadata and content.
 *
 * @param slidesService - Slides API service instance
 * @param presentationId - ID of the presentation
 * @returns Presentation object
 */
export async function getPresentation(
  slidesService: slides_v1.Slides,
  presentationId: string
): Promise<slides_v1.Schema$Presentation> {
  const response = await slidesService.presentations.get({
    presentationId,
  });

  return response.data;
}

export interface SlideInfo {
  slideNumber: number;
  objectId: string;
  textContent: string[];
}

export interface PresentationSummary {
  title: string | null | undefined;
  presentationId: string;
  slideCount: number;
  slides: SlideInfo[];
}

/**
 * Get a summary of the presentation.
 *
 * @param slidesService - Slides API service instance
 * @param presentationId - ID of the presentation
 * @returns Dictionary with presentation summary
 */
export async function getPresentationSummary(
  slidesService: slides_v1.Slides,
  presentationId: string
): Promise<PresentationSummary> {
  const presentation = await getPresentation(slidesService, presentationId);

  const summary: PresentationSummary = {
    title: presentation.title,
    presentationId,
    slideCount: presentation.slides?.length || 0,
    slides: [],
  };

  for (let idx = 0; idx < (presentation.slides || []).length; idx++) {
    const slide = presentation.slides![idx];
    const slideInfo: SlideInfo = {
      slideNumber: idx + 1,
      objectId: slide.objectId!,
      textContent: [],
    };

    // Extract text from slide elements
    for (const element of slide.pageElements || []) {
      if (element.shape?.text) {
        const textElements = element.shape.text.textElements || [];
        for (const textEl of textElements) {
          if (textEl.textRun) {
            const content = (textEl.textRun.content || '').trim();
            if (content) {
              slideInfo.textContent.push(content);
            }
          }
        }
      }
    }

    summary.slides.push(slideInfo);
  }

  return summary;
}

/**
 * Get all text content from a specific slide.
 *
 * @param slidesService - Slides API service instance
 * @param presentationId - ID of the presentation
 * @param slideIndex - Index of the slide (0-based)
 * @returns List of text strings from the slide
 */
export async function getSlideText(
  slidesService: slides_v1.Slides,
  presentationId: string,
  slideIndex: number = 0
): Promise<string[]> {
  const presentation = await getPresentation(slidesService, presentationId);
  const slides = presentation.slides || [];

  if (slideIndex >= slides.length) {
    return [];
  }

  const slide = slides[slideIndex];
  const textContent: string[] = [];

  for (const element of slide.pageElements || []) {
    if (element.shape?.text) {
      const textElements = element.shape.text.textElements || [];
      for (const textEl of textElements) {
        if (textEl.textRun) {
          const content = (textEl.textRun.content || '').trim();
          if (content) {
            textContent.push(content);
          }
        }
      }
    }
  }

  return textContent;
}

/**
 * Get all text content from the entire presentation.
 *
 * @param slidesService - Slides API service instance
 * @param presentationId - ID of the presentation
 * @returns Dictionary mapping slide numbers to text content
 */
export async function getAllPresentationText(
  slidesService: slides_v1.Slides,
  presentationId: string
): Promise<Record<number, string[]>> {
  const presentation = await getPresentation(slidesService, presentationId);
  const allText: Record<number, string[]> = {};

  for (let idx = 0; idx < (presentation.slides || []).length; idx++) {
    const slide = presentation.slides![idx];
    const slideText: string[] = [];

    for (const element of slide.pageElements || []) {
      if (element.shape?.text) {
        const textElements = element.shape.text.textElements || [];
        for (const textEl of textElements) {
          if (textEl.textRun) {
            const content = (textEl.textRun.content || '').trim();
            if (content) {
              slideText.push(content);
            }
          }
        }
      }
    }

    allText[idx + 1] = slideText;
  }

  return allText;
}

// ==================== UPDATE PRESENTATIONS (Section 5.3) ====================

export type PredefinedLayout = 'BLANK' | 'TITLE' | 'TITLE_AND_BODY' | 'TITLE_AND_TWO_COLUMNS' | 'TITLE_ONLY' | 'SECTION_HEADER' | 'SECTION_TITLE_AND_DESCRIPTION' | 'ONE_COLUMN_TEXT' | 'MAIN_POINT' | 'BIG_NUMBER';

/**
 * Add a new slide to the presentation.
 *
 * @param slidesService - Slides API service instance
 * @param presentationId - ID of the presentation
 * @param layout - Slide layout (BLANK, TITLE, TITLE_AND_BODY, etc.)
 * @param insertionIndex - Position to insert (undefined = end)
 * @returns Created slide info
 */
export async function addSlide(
  slidesService: slides_v1.Slides,
  presentationId: string,
  layout: PredefinedLayout = 'BLANK',
  insertionIndex?: number
): Promise<slides_v1.Schema$CreateSlideResponse> {
  const request: slides_v1.Schema$Request = {
    createSlide: {
      slideLayoutReference: {
        predefinedLayout: layout,
      },
    },
  };

  if (insertionIndex !== undefined) {
    request.createSlide!.insertionIndex = insertionIndex;
  }

  const response = await slidesService.presentations.batchUpdate({
    presentationId,
    requestBody: { requests: [request] },
  });

  return response.data.replies![0].createSlide!;
}

/**
 * Delete a slide from the presentation.
 *
 * @param slidesService - Slides API service instance
 * @param presentationId - ID of the presentation
 * @param slideObjectId - Object ID of the slide to delete
 */
export async function deleteSlide(
  slidesService: slides_v1.Slides,
  presentationId: string,
  slideObjectId: string
): Promise<void> {
  const requests: slides_v1.Schema$Request[] = [
    {
      deleteObject: {
        objectId: slideObjectId,
      },
    },
  ];

  await slidesService.presentations.batchUpdate({
    presentationId,
    requestBody: { requests },
  });
}

/**
 * Add a text box to a slide.
 *
 * @param slidesService - Slides API service instance
 * @param presentationId - ID of the presentation
 * @param slideObjectId - Object ID of the slide
 * @param text - Text content
 * @param x - X position in points
 * @param y - Y position in points
 * @param width - Width in points
 * @param height - Height in points
 * @returns Created element info
 */
export async function addTextBox(
  slidesService: slides_v1.Slides,
  presentationId: string,
  slideObjectId: string,
  text: string,
  x: number = 100,
  y: number = 100,
  width: number = 300,
  height: number = 50
): Promise<slides_v1.Schema$BatchUpdatePresentationResponse> {
  const elementId = `textbox_${uuidv4().slice(0, 8)}`;

  const requests: slides_v1.Schema$Request[] = [
    {
      createShape: {
        objectId: elementId,
        shapeType: 'TEXT_BOX',
        elementProperties: {
          pageObjectId: slideObjectId,
          size: {
            width: { magnitude: width, unit: 'PT' },
            height: { magnitude: height, unit: 'PT' },
          },
          transform: {
            scaleX: 1,
            scaleY: 1,
            translateX: x,
            translateY: y,
            unit: 'PT',
          },
        },
      },
    },
    {
      insertText: {
        objectId: elementId,
        text,
      },
    },
  ];

  const response = await slidesService.presentations.batchUpdate({
    presentationId,
    requestBody: { requests },
  });

  return response.data;
}

/**
 * Replace all occurrences of text in the presentation.
 *
 * @param slidesService - Slides API service instance
 * @param presentationId - ID of the presentation
 * @param oldText - Text to find
 * @param newText - Replacement text
 * @returns Number of replacements
 */
export async function replaceTextInPresentation(
  slidesService: slides_v1.Slides,
  presentationId: string,
  oldText: string,
  newText: string
): Promise<number> {
  const requests: slides_v1.Schema$Request[] = [
    {
      replaceAllText: {
        containsText: {
          text: oldText,
          matchCase: true,
        },
        replaceText: newText,
      },
    },
  ];

  const response = await slidesService.presentations.batchUpdate({
    presentationId,
    requestBody: { requests },
  });

  const replies = response.data.replies || [];
  if (replies.length > 0) {
    return replies[0].replaceAllText?.occurrencesChanged || 0;
  }
  return 0;
}
