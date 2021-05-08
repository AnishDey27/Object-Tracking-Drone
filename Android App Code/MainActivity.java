package com.example.trackaiv1;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowManager;
import android.webkit.WebView;
import android.widget.Button;
import android.widget.RelativeLayout;
import android.widget.TextView;
import android.widget.Toast;

import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

public class MainActivity extends AppCompatActivity {
    public int counter = 0;
    int X1 ;
    int Y1 ;
    int X2 ;
    int Y2 ;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        this.getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN, WindowManager.LayoutParams.FLAG_FULLSCREEN);
        RelativeLayout myLayout =(RelativeLayout)findViewById(R.id.mylayout);
        Button trackbtn =(Button)findViewById(R.id.button);
        TextView status =(TextView)findViewById(R.id.textView);

        FirebaseDatabase.getInstance().getReference("checkpoint").setValue("track_abort");



        WebView stream =(WebView)findViewById(R.id.webView); 
		webView.loadData("<html><head><meta name='viewport' content='target-densitydpi=device-dpi,initial-scale=1,minimum-scale=1,user-scalable=yes'/></head><body><center><img src=\"http://192.168.0.101:8080/\" alt=\"Stream\" align=\"middle\"></center></body></html>", "text/html", null);
		//paste your ip and port.
		webView.getSettings().setBuiltInZoomControls(true);


        trackbtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                counter++;
                if(counter ==3){
                    FirebaseDatabase.getInstance().getReference("checkpoint").setValue("track_abort");
                    counter =0;
                    trackbtn.setText("Select");
                }

                if(counter == 1){
                    trackbtn.setText("Track");


                    myLayout.setOnTouchListener(new View.OnTouchListener() {
                        @Override
                        public boolean onTouch(View v, MotionEvent event) {
                            switch(event.getAction()) {
                                case MotionEvent.ACTION_DOWN:
                                    X1 = (int) event.getX();
                                    Y1 = (int) event.getY();

                                    FirebaseDatabase.getInstance().getReference("coordinates").child("X1").setValue(X1);
                                    FirebaseDatabase.getInstance().getReference("coordinates").child("Y1").setValue(Y1);

                                    break;

                                case MotionEvent.ACTION_MOVE:
                                    // touch move code
                                    break;

                                case MotionEvent.ACTION_UP:
                                    X2 = (int) event.getX();
                                    Y2 = (int) event.getY();
                                    FirebaseDatabase.getInstance().getReference("coordinates").child("X2").setValue(X2);
                                    FirebaseDatabase.getInstance().getReference("coordinates").child("Y2").setValue(Y2);

                                    break;
                            }
                            return true;
                        }
                    });







                }
                else if(counter == 2){
                    FirebaseDatabase.getInstance().getReference("checkpoint").setValue("track_proceed");
                    trackbtn.setText("Cancel");
                }
            }
        });



    }
}