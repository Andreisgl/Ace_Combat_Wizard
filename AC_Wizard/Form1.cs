namespace AC_Wizard
{
    using System;
    using System.Diagnostics;
    using System.IO;
    using System.Text;
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            Check_folders();
            btnOpenFile.Enabled = false;
        }

        private void textBox1_TextChanged(object sender, EventArgs e)
        {
            btnOpenFile.Text = textBox1.Text;
        }

        private void btnOpenFile_Click(object sender, EventArgs e)
        {
            //openFileDialog1 = new OpenFileDialog();
            openFileDialog1.ShowDialog();
        }

        private void openFileDialog1_FileOk(object sender, System.ComponentModel.CancelEventArgs e)
        {
            label1.Text = openFileDialog1.FileName;
            //Process.Start(openFileDialog1.FileName);
        }

        private string project_path = "";
        private string PROJECT_FOLDER = "Projects";
        private void Check_folders()
        {
            string cwd = Directory.GetCurrentDirectory();
            PROJECT_FOLDER = cwd + "\\" + PROJECT_FOLDER;
            if(!Directory.Exists(PROJECT_FOLDER))
            {
                Directory.CreateDirectory(PROJECT_FOLDER);
            }
            projectBrowserDialog1.InitialDirectory = PROJECT_FOLDER;
        }
        private void btnOpenProject_Click(object sender, EventArgs e)
        {
            var Proj_Check = new Project_Checking();
            if (projectBrowserDialog1.ShowDialog() == DialogResult.OK)
            {
                project_path = projectBrowserDialog1.SelectedPath;
                label2.Text = PROJECT_FOLDER;
                btnOpenFile.Enabled = true;
                if (Proj_Check.Is_Project(project_path))
                {
                    label2.Text = "YAY!";
                }
                else
                {
                    label2.Text = "NOO!";
                }
            }
        }
        
    }
}