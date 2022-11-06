namespace AC_Wizard
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        private void Form1_Load(object sender, EventArgs e)
        {

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
        }
    }
}