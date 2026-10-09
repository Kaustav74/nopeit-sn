package com.air1.jeeapp

import android.annotation.SuppressLint
import android.app.Activity
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.webkit.*
import android.widget.EditText
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private var fileUploadCallback: ValueCallback<Array<Uri>>? = null

    // Default to active computer Wi-Fi address (192.168.1.9:8000)
    private var appUrl = "http://192.168.1.9:8000"

    private val filePickerLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == Activity.RESULT_OK && result.data != null) {
            val clipData = result.data?.clipData
            val dataUri = result.data?.data

            val results: Array<Uri>? = when {
                clipData != null -> {
                    Array(clipData.itemCount) { i -> clipData.getItemAt(i).uri }
                }
                dataUri != null -> {
                    arrayOf(dataUri)
                }
                else -> null
            }
            fileUploadCallback?.onReceiveValue(results)
        } else {
            fileUploadCallback?.onReceiveValue(null)
        }
        fileUploadCallback = null
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val prefs = getSharedPreferences("jee_air1_prefs", Context.MODE_PRIVATE)
        appUrl = prefs.getString("server_url", "http://192.168.1.9:8000") ?: "http://192.168.1.9:8000"

        webView = WebView(this).apply {
            settings.apply {
                javaScriptEnabled = true
                domStorageEnabled = true
                databaseEnabled = true
                allowFileAccess = true
                allowContentAccess = true
                useWideViewPort = true
                loadWithOverviewMode = true
                setSupportZoom(true)
                builtInZoomControls = false
                cacheMode = WebSettings.LOAD_DEFAULT
            }

            webViewClient = object : WebViewClient() {
                override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                    val url = request?.url?.toString() ?: return false
                    if (url.startsWith("https://calendar.google.com")) {
                        // Open Google Calendar in native intent
                        val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
                        startActivity(intent)
                        return true
                    }
                    return false
                }

                override fun onReceivedError(view: WebView?, request: WebResourceRequest?, error: WebResourceError?) {
                    super.onReceivedError(view, request, error)
                    if (request?.isForMainFrame == true) {
                        showServerConfigDialog()
                    }
                }
            }

            webChromeClient = object : WebChromeClient() {
                override fun onShowFileChooser(
                    webView: WebView?,
                    filePathCallback: ValueCallback<Array<Uri>>?,
                    fileChooserParams: FileChooserParams?
                ): Boolean {
                    fileUploadCallback?.onReceiveValue(null)
                    fileUploadCallback = filePathCallback

                    val intent = fileChooserParams?.createIntent() ?: Intent(Intent.ACTION_GET_CONTENT).apply {
                        type = "*/*"
                        putExtra(Intent.EXTRA_MIME_TYPES, arrayOf("application/pdf", "image/*", "text/*"))
                    }

                    try {
                        filePickerLauncher.launch(intent)
                    } catch (e: Exception) {
                        fileUploadCallback?.onReceiveValue(null)
                        fileUploadCallback = null
                        Toast.makeText(this@MainActivity, "Could not open file picker", Toast.LENGTH_SHORT).show()
                        return false
                    }
                    return true
                }
            }
        }

        setContentView(webView)
        webView.loadUrl(appUrl)
    }

    private fun showServerConfigDialog() {
        val input = EditText(this).apply {
            setText(appUrl)
            hint = "http://192.168.1.9:8000"
        }
        AlertDialog.Builder(this)
            .setTitle("JEE AIR-1 Server Connection")
            .setMessage("Unable to connect to $appUrl\n\nEnter your computer's IP address (e.g. http://192.168.1.9:8000) or local network address:")
            .setView(input)
            .setPositiveButton("Connect") { _, _ ->
                var newUrl = input.text.toString().trim()
                if (newUrl.isNotEmpty()) {
                    if (!newUrl.startsWith("http://") && !newUrl.startsWith("https://")) {
                        newUrl = "http://$newUrl"
                    }
                    appUrl = newUrl
                    getSharedPreferences("jee_air1_prefs", Context.MODE_PRIVATE)
                        .edit().putString("server_url", appUrl).apply()
                    webView.loadUrl(appUrl)
                }
            }
            .setNegativeButton("Retry") { _, _ ->
                webView.loadUrl(appUrl)
            }
            .setCancelable(true)
            .show()
    }

    override fun onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }
}
