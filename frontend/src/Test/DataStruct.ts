
//Demo2(柱状图方差累计贡献)数据结构
export interface demo2DataStruct {
    xAxis: string[];
    bar: number[];
    line: number[];
}

//Demo3(肘部法轮廓发系数)数据结构
export interface demo3DataStruct {
   K:number[];
   wcss:number[];
   silhouette:number[];
}

//Demo4(学生类型柱状图)数据结构
export interface demo4DataStruct {
    labels: string[];
    values: number[];
}

//Demo5(二维主成分影响图)数据结构
export interface demo5DataStruct {
    pca_scatter: {
        pc1: number;
        pc2: number;
        student_persona: string;
    }[];
}

//Demo6(三维主成分影响图)数据结构
export interface demo6DataStruct {
    pca_3d_scatter: {
        pc1: number;
        pc2: number;
        pc3: number;
        student_persona: string;
    }[];
}

//Demo7(各个方面的满意度)数据结构
export interface demo7DataStruct {
    [category: string]: {
        labels: string[];
        values: number[];
    };
}


//Demo8(热力图)数据结构
export interface demo8DataStruct {
    labels: string[];
    values: number[][];
}

//Demo9(整体满意度)数据结构
export interface demo9DataStruct {
   labels: string[];
   series: {
         name: string;
         data: number[];
   }
}

//Demo10(整体满意分布)数据结构
export interface demo10DataStruct {
    labels: string[];
    values: number[];
}

//Demo11(满意度贡献值)
export interface demo11DataStruct {
    labels: string[];
    values: number[];
}

