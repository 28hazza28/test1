using OpenGL;
using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using Emgu.CV;
using Emgu.CV.CvEnum;
using Emgu.CV.Structure;

namespace _3dMapOfCapture
{
    public struct Paint_in_GL
    {
        public Point3d_GL[] koord;
        public Point3d_GL[] norm;
        public Point3d_GL[] p1;
        public Point3d_GL[] p2;
        public Point3d_GL[] p3;
        public double red;
        public double green;
        public double blue;
        public double alpha;
        public float size;
        public PrimitiveType type;
        public string name;
        public Paint_in_GL( 
            double _red, double _green, double _blue,
            float _size, PrimitiveType _type, string _name, double _alpha = 0.1,
            Point3d_GL[] _norm = null, Point3d_GL[] _p1 = null, Point3d_GL[] _p2 = null, Point3d_GL[] _p3 = null, Point3d_GL[] _koord = null)
        {
            koord = _koord;
            red = _red;
            green = _green;
            blue = _blue;
            size = _size;
            type = _type;
            name = _name;
            alpha = _alpha;
            norm = _norm;
            p1 = _p1;
            p2 = _p2;
            p3 = _p3;
        }
    }

    public struct STLmodel
    {
        public string path;
        public double[,] koords;
        public STLmodel(string _path)
        {
            path = _path;
            koords = new double[50, 1];
        }
        public double parseE(string num)
        {
            var splnum = num.Split(new char[] { 'e' });
            return Convert.ToDouble(splnum[0]) * Math.Pow(10, Convert.ToInt32(splnum[1]));
        }
        public List<double[,]> parsingStl(string path)
        {
            int i2 = 0;
            string file1;
            List<double[,]> ret1 = new List<double[,]>();
            using (StreamReader sr = new StreamReader(path, ASCIIEncoding.ASCII))
            {
                file1 = sr.ReadToEnd();
            }
            string[] lines = file1.Split(new char[] { '\n' });
            double[,] norm = new double[(int)(lines.Length / 7), 3];
            double[,] p1   = new double[(int)(lines.Length / 7), 3];
            double[,] p2   = new double[(int)(lines.Length / 7), 3];
            double[,] p3   = new double[(int)(lines.Length / 7), 3];
            Console.WriteLine((int)(lines.Length / 7));
            Console.WriteLine("-------------------");
            int i3 = 0;
            foreach (string str in lines)
            {
                string ver = str.Trim();
                string[] vert = ver.Split(new char[] { ' ' });
                if (vert.Length > 3)
                {
                    if (vert[1].Contains("orma"))
                    {
                        norm[i2, 0] = parseE(vert[2]);
                        norm[i2, 1] = parseE(vert[3]);
                        norm[i2, 2] = parseE(vert[4]);
                        
                        i3 = 0;
                    }
                    else if (vert[0].Contains("ert") && i3 == 0)
                    {
                        p1[i2, 0] = parseE(vert[1]);
                        p1[i2, 1] = parseE(vert[2]);
                        p1[i2, 2] = parseE(vert[3]);
                        i3++;
                    }
                    else if (vert[0].Contains("ert") && i3 == 1)
                    {
                        p2[i2, 0] = parseE(vert[1]);
                        p2[i2, 1] = parseE(vert[2]);
                        p2[i2, 2] = parseE(vert[3]);
                        i3++;
                    }
                    else if (vert[0].Contains("ert") && i3 == 2)
                    {
                        p3[i2, 0] = parseE(vert[1]);
                        p3[i2, 1] = parseE(vert[2]);
                        p3[i2, 2] = parseE(vert[3]);
                        i2++;
                    }
                }
            }
        
            Console.WriteLine("-------------------");
            Console.WriteLine(i2);
            koords = p1;
            ret1.Add(norm);
            ret1.Add(p1);
            ret1.Add(p2);
            ret1.Add(p3);

            return ret1;
        }
    }
    class GraphicGL
    {
         double zoom = 0.1;
         double xRot = 2200;
         double yRot = 0;
         double zRot = 1200;
         double off_x = 0;
         double off_y = 0;

         public List<Paint_in_GL> all_obj = new List<Paint_in_GL>();
         public List<Point> all_points = new List<Point>();
         public List<Point> all_points_2 = new List<Point>();
         Point lastPos;

        public void GL_paint_3(List<Paint_in_GL> v1)
        {
            try
            {
                foreach (Paint_in_GL v in v1)
                {
               
                    Gl.LineWidth(v.size);
                    Gl.PointSize(v.size);
                    Gl.Color4(v.red, v.green, v.blue, v.alpha);
                    Gl.Begin(v.type);
              
                    int len = v.koord.Length;
                    for (var i = 0; i < len; i++)
                    {
                        Point3d_GL Norm1 = new Point3d_GL(0,0,0);
                        if (i<len-3)
                        {
                            Point3d_GL U = v.koord[i + 2] - v.koord[i];
                            Point3d_GL V = v.koord[i + 1] - v.koord[i];
                            Point3d_GL Norm = new Point3d_GL(
                                U.y * V.z - U.z * V.y,
                                U.z * V.x - U.x * V.z,
                                U.x * V.y - U.y * V.x);
                            Norm1 = Norm.normalize();
                        }
                        
                        Gl.Normal3(Norm1.x, Norm1.y, Norm1.z);
                        Gl.Vertex3(v.koord[i].x, v.koord[i].y, v.koord[i].z);
                    }
                    Gl.End();
                }
            }
            catch
            {
            }
        }
        public void GL_paint(List<Paint_in_GL> v1)
        {
            try
            {
                foreach (Paint_in_GL v in v1)
                {
                    Gl.LineWidth(v.size);
                    Gl.PointSize(v.size);
                    Gl.Color3(v.red, v.green, v.blue);
                    Gl.Begin(v.type);
                    int len = v.norm.Length;
                    for (var i = 0; i < len; i++)
                    {
                        Gl.Normal3(v.norm[i].x, v.norm[i].y, v.norm[i].z);
                        Gl.Vertex3(v.p1[i].x, v.p1[i].y, v.p1[i].z);
                        Gl.Vertex3(v.p2[i].x, v.p2[i].y, v.p2[i].z);
                        Gl.Vertex3(v.p3[i].x, v.p3[i].y, v.p3[i].z);
                    }
                    Gl.End();
                    Gl.PointSize(10.0f);
                    Gl.Color3(1.0f, 0, 0);
                    Gl.Begin(PrimitiveType.Points);
                    Gl.Vertex3(2.0f, 129.0f, 62.0f);
                    Gl.End();
                }
            }
            catch
            {
            }
        }
        public void GL_paint_2()
        {
        
            Gl.LoadIdentity();
            Gl.Clear(ClearBufferMask.ColorBufferBit | ClearBufferMask.DepthBufferBit);
            Gl.Translate(off_x, off_y, -250.0f);
            Gl.Scale(zoom, zoom, zoom);
            Gl.Rotate(xRot, 1, 0, 0);
            Gl.Rotate(yRot, 0, 1, 0);
            Gl.Rotate(zRot, 0, 0, 1);
            //Gl.MatrixMode(MatrixMode.Modelview);
            
        

        }
         public void glControl1_Render(object sender, GlControlEventArgs e)
        {
            Control senderControl = (Control)sender;
            Gl.Viewport(0, 0, senderControl.ClientSize.Width, senderControl.ClientSize.Height);
            GL_paint_2();
            GL_paint(all_obj);
           
        }
        public void glControl1_ContextCreated(object sender, GlControlEventArgs e)
        {

            Control senderControl = (Control)sender;
            Gl.Clear(ClearBufferMask.ColorBufferBit | ClearBufferMask.DepthBufferBit);
            Gl.MatrixMode(MatrixMode.Projection);
            Gl.LoadIdentity();
            Gl.Ortho(-10.0, 10.0, -10.0, 10.0, 0.0, 5000.0);
            //Gl.Ortho(-1.0, 1.0, -1.0, 1.0, 10.0, -10.0);
            Gl.MatrixMode(MatrixMode.Modelview);

        }
        public void glControl1_Load(object sender, EventArgs e)
        {
            Gl.Initialize();
            Gl.ClearColor(1.0f, 1.0f, 1.0f, 0.0f);
           // Gl.ShadeModel(ShadingModel.Flat);
            Gl.Enable(EnableCap.DepthTest);
            Gl.Enable(EnableCap.CullFace);
            Gl.Enable(EnableCap.Lighting);
            Gl.Light(LightName.Light0, LightParameter.Position, new float[] { 2.0f, 129.0f, 62.0f});
           Gl.Light(LightName.Light0, LightParameter.Diffuse, new float[] { 1.0f, 0.0f, 0.0f});
            Gl.Enable(EnableCap.Light0);
           // Gl.EnableClientState(EnableCap.VertexArray);
           //Gl.DepthRange(1, 0);

        }
        public void glControl1_MouseDown(object sender, MouseEventArgs e)
        {
            lastPos = e.Location;
        }
        public void glControl1_MouseMove(object sender, MouseEventArgs e)
        {
            Control senderControl = (Control)sender;
            var dx = e.X - lastPos.X;
            var dy = e.Y - lastPos.Y;
            double dyx = lastPos.Y - senderControl.ClientSize.Width / 2;
            double dxy = lastPos.X - senderControl.ClientSize.Height / 2;
            double dz = (dy * dxy + dx * dyx) / (Math.Sqrt(dy * dy + dx * dx) * Math.Sqrt(dxy * dxy + dyx * dyx));
            if (e.Button == MouseButtons.Left)
            {
                xRot += dy;
                //yRot += dz;
                zRot += dx;
            }
            else if (e.Button == MouseButtons.Right)
            {
                off_x += Convert.ToDouble(dx) / 360;
                off_y += Convert.ToDouble(dy) / 360;
            }
            lastPos = e.Location;
        }
        public void Form1_mousewheel(object sender, MouseEventArgs e)
        {
            var angle = e.Delta;
            if (angle < 0)
            {
                if (zoom < 0.002)
                {
                }
                else
                {
                    zoom = 0.7 * zoom;
                    zoom = Math.Round(zoom, 4);
                }
            }
            else
            {
                zoom = 1.3 * zoom;
                zoom = Math.Round(zoom, 4);
            }
        }
    }
    
}
