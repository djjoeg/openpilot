python3 - <<'EOF'
p='viewer3d_page.html'; s=open(p).read()
rep=[
('''  const LVS = `
    attribute vec3 aPos;
    uniform mat4 uProj; uniform mat4 uView; uniform mat3 uRot; uniform vec3 uOff;
    void main() { gl_Position = uProj * (uView * vec4(uRot * (aPos + uOff), 1.0)); }`;''',
'''  // the outlines are drawn a hair nearer than the faces (0.2 % of the way to the eye), so they show on their own
  // faces but not through anything in front of them
  const LVS = `
    attribute vec3 aPos;
    uniform mat4 uProj; uniform mat4 uView; uniform mat3 uRot; uniform vec3 uOff;
    void main() {
      vec4 p = uView * vec4(uRot * (aPos + uOff), 1.0);
      p.xyz *= 0.998;
      gl_Position = uProj * p;
    }`;'''),
('''    gl.uniform1f(P.u.uPick, 0);
    gl.enable(gl.POLYGON_OFFSET_FILL);
    gl.polygonOffset(1, 1);
    for (const p of parts) {''','''    gl.uniform1f(P.u.uPick, 0);
    for (const p of parts) {'''),
('''    gl.disable(gl.POLYGON_OFFSET_FILL);
    // their outlines''','''    // their outlines'''),
]
for a,b in rep:
  assert a in s, a[:50]; s=s.replace(a,b)
open(p,'w').write(s)
EOF
grep -n "POLYGON_OFFSET\|0.998" viewer3d_page.html