python3 - <<'EOF'
p='viewer3d_page.html'; s=open(p).read()
rep=[
('''    const lp = new Float32Array(lines.length * 3);
    for (let i = 0; i < lines.length; i++) { const v = lines[i]; lp[3 * i] = pos[3 * v]; lp[3 * i + 1] = pos[3 * v + 1]; lp[3 * i + 2] = pos[3 * v + 2]; }''',
'''    // each outline corner carries the other end of its edge too, so the shader can drop edges seen end-on
    const lp = new Float32Array(lines.length * 6);
    for (let i = 0; i < lines.length; i++) {
      const v = lines[i], w = lines[i ^ 1];
      lp.set([pos[3 * v], pos[3 * v + 1], pos[3 * v + 2], pos[3 * w], pos[3 * w + 1], pos[3 * w + 2]], 6 * i);
    }'''),
('''  // the outlines are drawn a hair nearer than the faces (0.2 % of the way to the eye), so they show on their own
  // faces but not through anything in front of them
  const LVS = `
    attribute vec3 aPos;
    uniform mat4 uProj; uniform mat4 uView; uniform mat3 uRot; uniform vec3 uOff;
    void main() {
      vec4 p = uView * vec4(uRot * (aPos + uOff), 1.0);
      p.xyz *= 0.998;
      gl_Position = uProj * p;
    }`;''',
'''  // the outlines are drawn a hair nearer than the faces (0.2 % of the way to the eye), so they show on their own
  // faces but not through anything in front of them; an edge seen end-on (under 1.5 px long) is left out
  const LVS = `
    attribute vec3 aPos; attribute vec3 aOther;
    uniform mat4 uProj; uniform mat4 uView; uniform mat3 uRot; uniform vec3 uOff; uniform vec2 uVp;
    void main() {
      vec4 p = uView * vec4(uRot * (aPos + uOff), 1.0);
      vec4 q = uView * vec4(uRot * (aOther + uOff), 1.0);
      p.xyz *= 0.998; q.xyz *= 0.998;
      vec4 cp = uProj * p, cq = uProj * q;
      gl_Position = cp;
      if (cp.w > 0.0 && cq.w > 0.0) {
        vec2 d = (cp.xy / cp.w - cq.xy / cq.w) * 0.5 * uVp;
        if (dot(d, d) < 2.25) gl_Position = vec4(2.0, 2.0, 2.0, 1.0);
      }
    }`;'''),
('''    gl.bindAttribLocation(p, 1, "aNrm");''', '''    gl.bindAttribLocation(p, 1, vs.includes("aOther") ? "aOther" : "aNrm");'''),
('''    gl.uniformMatrix3fv(prog.u.uRot, false, ROT);
    if (prog.u.uNrmM) {''', '''    gl.uniformMatrix3fv(prog.u.uRot, false, ROT);
    if (prog.u.uVp) gl.uniform2f(prog.u.uVp, W, H);
    if (prog.u.uNrmM) {'''),
('''  function bindLine(m) {
    gl.bindBuffer(gl.ARRAY_BUFFER, m.line);
    gl.enableVertexAttribArray(0);
    gl.disableVertexAttribArray(1);
    gl.vertexAttribPointer(0, 3, gl.FLOAT, false, 12, 0);
  }''', '''  function bindLine(m) {
    gl.bindBuffer(gl.ARRAY_BUFFER, m.line);
    gl.enableVertexAttribArray(0);
    gl.enableVertexAttribArray(1);
    gl.vertexAttribPointer(0, 3, gl.FLOAT, false, 24, 0);
    gl.vertexAttribPointer(1, 3, gl.FLOAT, false, 24, 12);
  }'''),
]
for a,b in rep:
  assert a in s, a[:50]; s=s.replace(a,b)
open(p,'w').write(s)
EOF
export PYTHONPATH=/home/claude/pylib && timeout 600 python3 viewer3d.py && cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v3d && python3 wrap.py /home/claude/deliver/hardware/report/arm-3d.html page2.html && timeout 120 node speck.js && python3 -c "
from PIL import Image
Image.open('sp-all.png').resize((520,280), Image.NEAREST).save('sp-big3.png')"