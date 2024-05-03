package net.keimag.hakoirimusume;

public class ImgurAnonymousUploaderTest {
    public static void main(String[] args) {
        ImgurAnonymousUploader uploader = new ImgurAnonymousUploader("{{IMGUR_CLIENT_ID}}");
        try {
            var response = uploader.uploadFile(new java.io.File("testimage.jpg"), "Test Image", "This is a test image.");
            System.out.println(response);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
