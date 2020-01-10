package com.diy.edu.rd.ui;

import android.os.Handler;
import android.os.Message;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.TextView;

import com.chaquo.python.Kwarg;
import com.chaquo.python.PyObject;
import com.chaquo.python.android.AndroidPlatform;
import com.chaquo.python.Python;
import com.diy.edu.rd.Model.JavaBean;
import com.test.R;
import com.diy.edu.rd.utils.GlobalFunction;
import com.diy.edu.rd.utils.GlobalVariables;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

public class TestActivity extends AppCompatActivity {
    static final String TAG = "PythonOnAndroid";
    private TextView tvRun;
    private TextView tvInfo;
    private String modulePath;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_test);
        GlobalVariables.tac = this;
        initView();
        initPython();
        copFiles();
//        callPythonCode();
    }

    private void initView() {
        tvRun = (TextView)findViewById(R.id.tv_run);
        tvInfo = (TextView)findViewById(R.id.tv_info);
        tvRun.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                runModel();
            }
        });
    }

    private void copFiles(){
        String fileName = "test_data.txt";
        String destFile = GlobalFunction.getFolder(GlobalVariables.TEMP,"")+fileName;
        if(!new File(destFile).exists()){
            GlobalFunction.copyFile(this,fileName,destFile);
        }

        fileName = "test_label.txt";
        destFile = GlobalFunction.getFolder(GlobalVariables.TEMP,"")+fileName;
        if(!new File(destFile).exists()){
            GlobalFunction.copyFile(this,fileName,destFile);
        }

        fileName = "train_data.txt";
        destFile = GlobalFunction.getFolder(GlobalVariables.TEMP,"")+fileName;
        if(!new File(destFile).exists()){
            GlobalFunction.copyFile(this,fileName,destFile);
        }

        fileName = "train_label.txt";
        destFile = GlobalFunction.getFolder(GlobalVariables.TEMP,"")+fileName;
        if(!new File(destFile).exists()){
            GlobalFunction.copyFile(this,fileName,destFile);
        }
    }
    // 初始化Python环境
    void initPython(){
        if (! Python.isStarted()) {
            Python.start(new AndroidPlatform(this));
        }
    }

    public void sendMessage(String content){
        Message msg = new Message();
        msg.what=1;
        msg.obj = content;
        handler.sendMessage(msg);
    }

    private void runModel(){
        new Thread(new Runnable() {
            @Override
            public void run() {
                try{
                    Python py = Python.getInstance();
                    String path = GlobalFunction.getFolder(GlobalVariables.TEMP,"").replace("\\","/");
                    modulePath = path+"models/";
                    File file = new File(modulePath);
                    if(!file.exists()){
                        file.mkdirs();
                    }
                    py.getModule("run").callAttr("doRun",path);
                }catch(Exception ex){
                    ex.printStackTrace();
                }finally {
                    sendMessage("------------------------->运行结束<--------------------");
                }

            }
        }).start();


    }

    Handler handler = new Handler() {
        public void handleMessage(android.os.Message msg) {
            switch (msg.what) {
                case 0:
                    GlobalFunction.showToast(TestActivity.this,"执行完毕,请到:"+modulePath+"下查看数据");
                    break;
                case 1:
                    String content = msg.obj.toString()+"\n";
                    tvInfo.append(content);
                    break;
                default:
                    break;
            }
        }

        ;
    };

    // 调用python代码
    void callPythonCode(){
        Python py = Python.getInstance();
        String path = GlobalFunction.getFolder(GlobalVariables.TEMP,"").replace("\\","/");
        String modulePath = path+"models/";
        File file = new File(modulePath);
        if(!file.exists()){
            file.mkdirs();
        }
        py.getModule("run").callAttr("doRun",path);
        // 调用test.py模块中的greet函数，并传一个参数
        // 等价用法：py.getModule("test").get("greet").call("Android");
        py.getModule("test").callAttr("greet", "Android");

        // 调用python内建函数help()，输出了帮助信息
        py.getBuiltins().get("help").call();

        PyObject obj1 = py.getModule("test").callAttr("add", 2,3);
        // 将Python返回值换为Java中的Integer类型
        Integer sum = obj1.toJava(Integer.class);
        Log.d(TAG,"add = "+sum.toString());

        // 调用python函数，命名式传参，等同 sub(10,b=1,c=3)
        PyObject obj2 = py.getModule("test").callAttr("sub", 10,new Kwarg("b", 1), new Kwarg("c", 3));
        Integer result = obj2.toJava(Integer.class);
        Log.d(TAG,"sub = "+result.toString());

        // 调用Python函数，将返回的Python中的list转为Java的list
        PyObject obj3 = py.getModule("test").callAttr("get_list", 10,"xx",5.6,'c');
        List<PyObject> pyList = obj3.asList();
        Log.d(TAG,"get_list = "+pyList.toString());

        // 将Java的ArrayList对象传入Python中使用
        List<PyObject> params = new ArrayList<PyObject>();
        params.add(PyObject.fromJava("alex"));
        params.add(PyObject.fromJava("bruce"));
        py.getModule("test").callAttr("print_list", params);

        // Python中调用Java类
        PyObject obj4 = py.getModule("test").callAttr("get_java_bean");
        JavaBean data = obj4.toJava(JavaBean.class);
        data.print();
    }
}
