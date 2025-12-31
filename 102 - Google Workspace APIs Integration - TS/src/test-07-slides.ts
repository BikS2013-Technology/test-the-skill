/**
 * Test script for: Slides API Functions
 * From document: 102 - Google-Workspace-APIs-Integration-Guide-ts.md
 * Document lines: 2284-2698 (Section 5)
 *
 * Tests: Create, Read, Update Presentations
 */
import { getDriveService, getSlidesService } from './google-workspace-auth';
import { deleteFile } from './drive-api';
import {
  createPresentation,
  createPresentationWithSlides,
  getPresentation,
  getPresentationSummary,
  getSlideText,
  getAllPresentationText,
  addSlide,
  deleteSlide,
  addTextBox,
  replaceTextInPresentation,
} from './slides-api';

const CREDENTIALS_PATH = '/Users/giorgosmarinos/.google-skills/drive/DriveSkill-Credentials.json';
const TOKEN_PATH = '/Users/giorgosmarinos/.google-skills/drive/token.json';

async function testSlidesAPI(): Promise<void> {
  console.log('=' .repeat(60));
  console.log('Test: Slides API Functions');
  console.log('=' .repeat(60));

  const driveService = await getDriveService(CREDENTIALS_PATH, TOKEN_PATH);
  const slidesService = await getSlidesService(CREDENTIALS_PATH, TOKEN_PATH);
  console.log('[OK] Drive and Slides services initialized');

  const createdPresentationIds: string[] = [];

  try {
    // ==================== CREATE PRESENTATIONS (Section 5.1) ====================
    console.log('\n--- CREATE PRESENTATIONS (Section 5.1) ---');

    // Test: createPresentation
    console.log('\n[Test] createPresentation()');
    const timestamp = Date.now();
    const pres1 = await createPresentation(slidesService, `TestPresentation-${timestamp}`);
    createdPresentationIds.push(pres1.presentationId!);
    console.log(`[OK] Created presentation: ${pres1.presentationId}`);
    console.log(`     Title: ${pres1.title}`);

    // Test: createPresentationWithSlides
    console.log('\n[Test] createPresentationWithSlides()');
    const pres2 = await createPresentationWithSlides(slidesService, `MultiSlidePresentation-${timestamp}`, 5);
    createdPresentationIds.push(pres2.presentationId!);
    console.log(`[OK] Created presentation with slides: ${pres2.presentationId}`);

    // ==================== READ PRESENTATIONS (Section 5.2) ====================
    console.log('\n--- READ PRESENTATIONS (Section 5.2) ---');

    // Test: getPresentation
    console.log('\n[Test] getPresentation()');
    // Fetch the multi-slide presentation to see all slides
    const fetchedPres = await getPresentation(slidesService, pres2.presentationId!);
    console.log(`[OK] Fetched presentation: ${fetchedPres.title}`);
    console.log(`     Slides: ${fetchedPres.slides?.length}`);

    // Test: getPresentationSummary
    console.log('\n[Test] getPresentationSummary()');
    const summary = await getPresentationSummary(slidesService, pres2.presentationId!);
    console.log(`[OK] Presentation summary: "${summary.title}"`);
    console.log(`     Slide count: ${summary.slideCount}`);
    for (const slide of summary.slides) {
      console.log(`     - Slide ${slide.slideNumber}: ${slide.objectId}`);
    }

    // Test: getSlideText (will be empty on blank slides)
    console.log('\n[Test] getSlideText()');
    const slideText = await getSlideText(slidesService, pres2.presentationId!, 0);
    console.log(`[OK] Slide 1 text content: ${slideText.length} text elements`);

    // Test: getAllPresentationText (will be empty on blank slides)
    console.log('\n[Test] getAllPresentationText()');
    const allText = await getAllPresentationText(slidesService, pres2.presentationId!);
    console.log(`[OK] Got text from ${Object.keys(allText).length} slides`);

    // ==================== UPDATE PRESENTATIONS (Section 5.3) ====================
    console.log('\n--- UPDATE PRESENTATIONS (Section 5.3) ---');

    // Test: addSlide
    console.log('\n[Test] addSlide()');
    const newSlide = await addSlide(slidesService, pres1.presentationId!, 'BLANK');
    console.log(`[OK] Added slide: ${newSlide.objectId}`);

    // Test: addTextBox
    console.log('\n[Test] addTextBox()');
    // Get the slide object ID for the first slide
    const updatedPres1 = await getPresentation(slidesService, pres1.presentationId!);
    const firstSlideId = updatedPres1.slides![0].objectId!;
    await addTextBox(
      slidesService,
      pres1.presentationId!,
      firstSlideId,
      'Hello from test! MARKER_TEXT',
      100,
      100,
      400,
      60
    );
    console.log(`[OK] Added text box to slide ${firstSlideId}`);

    // Verify text was added
    const textAfterAdd = await getSlideText(slidesService, pres1.presentationId!, 0);
    console.log(`     Text on slide after adding: ${textAfterAdd.join(', ')}`);

    // Test: replaceTextInPresentation
    console.log('\n[Test] replaceTextInPresentation()');
    const replacements = await replaceTextInPresentation(
      slidesService,
      pres1.presentationId!,
      'MARKER_TEXT',
      'REPLACED_TEXT'
    );
    console.log(`[OK] Replaced ${replacements} occurrences`);

    // Verify replacement
    const textAfterReplace = await getSlideText(slidesService, pres1.presentationId!, 0);
    console.log(`     Text after replacement: ${textAfterReplace.join(', ')}`);

    // Test: deleteSlide
    console.log('\n[Test] deleteSlide()');
    // Delete the second slide we added
    const presBeforeDelete = await getPresentation(slidesService, pres1.presentationId!);
    const slideCountBefore = presBeforeDelete.slides?.length || 0;
    const slideToDelete = presBeforeDelete.slides![1].objectId!;
    await deleteSlide(slidesService, pres1.presentationId!, slideToDelete);
    const presAfterDelete = await getPresentation(slidesService, pres1.presentationId!);
    console.log(`[OK] Deleted slide - count: ${slideCountBefore} -> ${presAfterDelete.slides?.length}`);

    console.log('\n' + '=' .repeat(60));
    console.log('Test: PASSED');
    console.log('=' .repeat(60));

  } finally {
    // Cleanup - delete all test presentations
    console.log('\n[Cleanup] Deleting test presentations...');

    for (const presentationId of createdPresentationIds) {
      try {
        await deleteFile(driveService, presentationId, true);
      } catch (e) {
        // Ignore cleanup errors
      }
    }

    console.log(`[OK] Cleaned up ${createdPresentationIds.length} presentations`);
  }
}

// Run the test
testSlidesAPI().catch((error) => {
  console.error('\n[ERROR] Test failed:', error.message);
  console.error(error);
  process.exit(1);
});
