package com.diy.edu.rd.Model;

import android.util.Log;

import com.diy.edu.rd.utils.GlobalVariables;

import java.util.ArrayList;
import java.util.List;

public class JavaBean {
    private String name;
    private List<String> data;

    public JavaBean(String n){
        this.name = n;
        data = new ArrayList<String>();
    }

    public void setData(String el){
        this.data.add(el);
    }

    public void print(){
        for (String it: data) {
            Log.d("Java Bean - "+this.name,it);
        }
    }

    public void println(String content){
        Log.d("Java Bean - ",content);
        try{
            GlobalVariables.tac.sendMessage(content);
        }catch (Exception ex){
            ex.printStackTrace();
        }
    }
}