// Geometry tests do not render pixels. Supply image dimensions to Three's loader;
// texture appearance is checked separately in the real browser.
globalThis.self??=globalThis;
globalThis.createImageBitmap??=async blob=>{
 const bytes=new Uint8Array(await blob.arrayBuffer());
 if(bytes[0]!==137||bytes[1]!==80)throw new Error('Expected embedded PNG pigment map');
 const view=new DataView(bytes.buffer);return {width:view.getUint32(16),height:view.getUint32(20),close(){}};
};
