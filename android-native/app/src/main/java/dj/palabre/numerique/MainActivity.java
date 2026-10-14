package dj.palabre.numerique;

import android.Manifest;
import android.app.Activity;
import android.os.Bundle;
import android.content.pm.PackageManager;
import android.webkit.PermissionRequest;
import android.webkit.WebChromeClient;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebResourceRequest;
import android.net.Uri;

public class MainActivity extends Activity {
    private static final String HOME = "https://palabre-numerique.vercel.app";
    private WebView webView;
    private PermissionRequest pendingRequest;
    private static final String AUDIO_RESOURCE = PermissionRequest.RESOURCE_AUDIO_CAPTURE;
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        webView = new WebView(this);
        setContentView(webView);
        webView.getSettings().setJavaScriptEnabled(true);
        webView.getSettings().setDomStorageEnabled(true);
        webView.getSettings().setMediaPlaybackRequiresUserGesture(true);
        webView.getSettings().setAllowFileAccess(false);
        webView.getSettings().setAllowContentAccess(false);
        android.webkit.WebView.setWebContentsDebuggingEnabled(false);
        webView.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri url = request.getUrl();
                if ("https".equalsIgnoreCase(url.getScheme()) && "palabre-numerique.vercel.app".equalsIgnoreCase(url.getHost())) return false;
                if ("http".equalsIgnoreCase(url.getScheme()) || "https".equalsIgnoreCase(url.getScheme())) {
                    startActivity(new android.content.Intent(android.content.Intent.ACTION_VIEW, url));
                }
                return true;
            }
        });
        webView.setWebChromeClient(new WebChromeClient() {
            @Override public void onPermissionRequest(PermissionRequest request) {
                runOnUiThread(() -> {
                    boolean audio = false;
                    for (String resource : request.getResources()) if (AUDIO_RESOURCE.equals(resource)) audio = true;
                    if (!audio || request.getResources().length != 1 || !HOME.equals(request.getOrigin().toString().replaceAll("/$", ""))) { request.deny(); return; }
                    pendingRequest = request;
                    if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
                        request.grant(new String[]{PermissionRequest.RESOURCE_AUDIO_CAPTURE});
                        pendingRequest = null;
                    } else requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO}, 77);
                });
            }
        });
        webView.loadUrl(HOME);
    }
    @Override public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] results) {
        super.onRequestPermissionsResult(requestCode, permissions, results);
        if (requestCode == 77 && pendingRequest != null) {
            if (results.length > 0 && results[0] == PackageManager.PERMISSION_GRANTED)
                pendingRequest.grant(new String[]{PermissionRequest.RESOURCE_AUDIO_CAPTURE});
            else pendingRequest.deny();
            pendingRequest = null;
        }
    }
    @Override public void onBackPressed() {
        if (webView.canGoBack()) webView.goBack(); else super.onBackPressed();
    }
    @Override protected void onDestroy() {
        if (pendingRequest != null) { pendingRequest.deny(); pendingRequest = null; }
        webView.destroy();
        super.onDestroy();
    }
}
